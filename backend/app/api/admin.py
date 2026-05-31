"""
Admin-only endpoints:
  GET  /admin/users          — lista de todos los usuarios
  PATCH /admin/users/{id}    — activar/desactivar / hacer admin
  GET  /admin/reviews        — todas las reseñas (con filtro is_approved)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.category import Review

router = APIRouter(prefix="/admin", tags=["admin"])

# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    q = db.query(User)
    if search:
        term = f"%{search}%"
        q = q.filter(
            (User.email.ilike(term))
            | (User.first_name.ilike(term))
            | (User.last_name.ilike(term))
        )
    total = q.count()
    users = q.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "phone": u.phone,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "is_verified": u.is_verified,
                "loyalty_points": u.loyalty_points,
                "created_at": u.created_at,
            }
            for u in users
        ],
    }


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "Usuario no encontrado")

    allowed = {"is_active", "is_admin", "loyalty_points"}
    for k, v in payload.items():
        if k in allowed:
            setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "is_active": user.is_active, "is_admin": user.is_admin}


# ── Reviews (global) ──────────────────────────────────────────────────────────

@router.get("/reviews")
def list_all_reviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    is_approved: Optional[bool] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    q = db.query(Review)
    if is_approved is not None:
        q = q.filter(Review.is_approved == is_approved)
    total = q.count()
    reviews = q.order_by(Review.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [
            {
                "id": r.id,
                "product_id": r.product_id,
                "user_id": r.user_id,
                "user_name": f"{r.user.first_name} {r.user.last_name}" if r.user else "—",
                "rating": r.rating,
                "title": r.title,
                "body": r.body,
                "is_approved": r.is_approved,
                "created_at": r.created_at,
            }
            for r in reviews
        ],
    }
