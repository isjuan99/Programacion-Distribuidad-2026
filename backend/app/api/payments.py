from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.wishlist import PaymentMethod

router = APIRouter(prefix="/users/me/payment-methods", tags=["payments"])

STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")


class PaymentMethodResponse(BaseModel):
    id: int
    stripe_payment_method_id: str
    last4: str
    brand: str
    exp_month: int
    exp_year: int
    is_default: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class AddPaymentMethodRequest(BaseModel):
    stripe_payment_method_id: str
    last4: str
    brand: str
    exp_month: int
    exp_year: int
    set_default: bool = False


@router.get("", response_model=List[PaymentMethodResponse])
async def list_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(PaymentMethod).filter(
        PaymentMethod.user_id == current_user.id
    ).order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc()).all()


@router.post("", response_model=PaymentMethodResponse, status_code=201)
async def add_payment_method(
    data: AddPaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.set_default:
        db.query(PaymentMethod).filter(
            PaymentMethod.user_id == current_user.id
        ).update({"is_default": False})

    pm = PaymentMethod(
        user_id=current_user.id,
        stripe_payment_method_id=data.stripe_payment_method_id,
        last4=data.last4,
        brand=data.brand,
        exp_month=data.exp_month,
        exp_year=data.exp_year,
        is_default=data.set_default,
    )
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


@router.delete("/{pm_id}", status_code=204)
async def delete_payment_method(
    pm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pm = db.query(PaymentMethod).filter(
        PaymentMethod.id == pm_id,
        PaymentMethod.user_id == current_user.id,
    ).first()
    if not pm:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    db.delete(pm)
    db.commit()


@router.put("/{pm_id}/default", response_model=PaymentMethodResponse)
async def set_default_payment_method(
    pm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(PaymentMethod).filter(
        PaymentMethod.user_id == current_user.id
    ).update({"is_default": False})
    pm = db.query(PaymentMethod).filter(
        PaymentMethod.id == pm_id,
        PaymentMethod.user_id == current_user.id,
    ).first()
    if not pm:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    pm.is_default = True
    db.commit()
    db.refresh(pm)
    return pm


@router.post("/setup-intent")
async def create_setup_intent(
    current_user: User = Depends(get_current_user),
):
    """Creates a Stripe Setup Intent client secret for frontend card collection."""
    if not STRIPE_SECRET or STRIPE_SECRET.startswith("sk_test_xxx"):
        return {"client_secret": None, "message": "Stripe no configurado"}
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET
        intent = stripe.SetupIntent.create(
            customer=None,
            payment_method_types=["card"],
            metadata={"user_id": str(current_user.id)},
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
