from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.returns import Return, ReturnStatus
from app.models.order import Order, OrderStatus
from app.models.wishlist import LoyaltyTransaction
from app.utils.email import send_return_status_email

router = APIRouter(prefix="/returns", tags=["returns"])


class ReturnCreate(BaseModel):
    order_id: int
    reason: str
    comments: Optional[str] = None
    images: Optional[List[str]] = None


class ReturnStatusUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None
    refund_amount: Optional[float] = None
    return_label_url: Optional[str] = None
    return_address: Optional[str] = None
    refund_type: Optional[str] = None  # 'card', 'points', 'exchange'


class TrackingUpdate(BaseModel):
    tracking_number: str


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    reason: str
    comments: Optional[str] = None
    images: Optional[List[str]] = None
    status: str
    admin_notes: Optional[str] = None
    refund_amount: Optional[float] = None
    return_label_url: Optional[str] = None
    return_address: Optional[str] = None
    tracking_number: Optional[str] = None
    refund_type: Optional[str] = None
    created_at: object
    model_config = {"from_attributes": True}


@router.post("", response_model=ReturnResponse, status_code=201)
async def create_return(
    data: ReturnCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(
        Order.id == data.order_id,
        Order.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.status != OrderStatus.delivered:
        raise HTTPException(status_code=400, detail="Solo puedes solicitar devolución de pedidos entregados")

    if order.updated_at:
        deadline = order.updated_at.replace(tzinfo=None) + timedelta(days=30)
        if datetime.utcnow() > deadline:
            raise HTTPException(status_code=400, detail="El periodo de devolución de 30 días ha expirado")

    existing = db.query(Return).filter(
        Return.order_id == data.order_id,
        Return.status.in_(['pending', 'approved']),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud de devolución activa para este pedido")

    ret = Return(
        order_id=data.order_id,
        user_id=current_user.id,
        reason=data.reason,
        comments=data.comments,
        images=data.images or [],
    )
    db.add(ret)
    db.commit()
    db.refresh(ret)
    return ret


@router.get("/my-returns", response_model=List[ReturnResponse])
async def my_returns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Return).filter(
        Return.user_id == current_user.id
    ).order_by(Return.created_at.desc()).all()


@router.get("", response_model=List[ReturnResponse])
async def admin_list_returns(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    query = db.query(Return).order_by(Return.created_at.desc())
    if status:
        query = query.filter(Return.status == status)
    return query.offset((page - 1) * per_page).limit(per_page).all()


@router.put("/{return_id}/tracking", response_model=ReturnResponse)
async def add_tracking_number(
    return_id: int,
    data: TrackingUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ret = db.query(Return).options(
        joinedload(Return.order), joinedload(Return.user)
    ).filter(
        Return.id == return_id,
        Return.user_id == current_user.id,
    ).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Devolución no encontrada")
    if ret.status != ReturnStatus.approved.value:
        raise HTTPException(status_code=400, detail="Solo puedes agregar guía a devoluciones aprobadas")

    ret.tracking_number = data.tracking_number
    ret.status = ReturnStatus.shipped.value
    db.commit()
    db.refresh(ret)

    background_tasks.add_task(
        send_return_status_email,
        ret.user.email,
        ret.user.first_name,
        ret.order.order_number,
        "shipped",
        tracking_number=data.tracking_number,
    )
    return ret


@router.put("/{return_id}/status", response_model=ReturnResponse)
async def update_return_status(
    return_id: int,
    data: ReturnStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    ret = db.query(Return).options(
        joinedload(Return.order), joinedload(Return.user)
    ).filter(Return.id == return_id).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Devolución no encontrada")

    valid_statuses = [s.value for s in ReturnStatus]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {valid_statuses}")

    ret.status = data.status
    if data.admin_notes is not None:
        ret.admin_notes = data.admin_notes
    if data.refund_amount is not None:
        ret.refund_amount = data.refund_amount
    if data.return_label_url is not None:
        ret.return_label_url = data.return_label_url
    if data.return_address is not None:
        ret.return_address = data.return_address
    if data.refund_type is not None:
        ret.refund_type = data.refund_type

    # Award loyalty points when refund type is 'points'
    if data.status == ReturnStatus.refunded.value and data.refund_type == "points" and data.refund_amount:
        points_earned = int(data.refund_amount / 10)
        if points_earned > 0:
            ret.user.loyalty_points = (ret.user.loyalty_points or 0) + points_earned
            tx = LoyaltyTransaction(
                user_id=ret.user_id,
                points=points_earned,
                type="earned",
                description=f"Reembolso por devolución — Pedido #{ret.order.order_number}",
            )
            db.add(tx)

    db.commit()
    db.refresh(ret)

    if data.status in ("approved", "rejected", "received", "refunded"):
        background_tasks.add_task(
            send_return_status_email,
            ret.user.email,
            ret.user.first_name,
            ret.order.order_number,
            data.status,
            data.admin_notes,
            return_address=data.return_address,
            return_label_url=data.return_label_url,
            refund_type=data.refund_type,
            refund_amount=data.refund_amount,
        )

    return ret
