from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.wishlist import Wishlist
from app.models.product import Product, ProductVariant

router = APIRouter(prefix="/users/me/wishlist", tags=["wishlist"])


class WishlistItemResponse(BaseModel):
    id: int
    product_id: int
    created_at: datetime
    product_name: str
    product_brand: str | None
    product_image: str | None
    product_price: float | None
    product_compare_price: float | None
    product_slug: str

    model_config = {"from_attributes": True}


@router.get("", response_model=List[WishlistItemResponse])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Wishlist)
        .options(joinedload(Wishlist.product).joinedload(Product.brand))
        .filter(Wishlist.user_id == current_user.id)
        .order_by(Wishlist.created_at.desc())
        .all()
    )
    result = []
    for item in items:
        p = item.product
        variant = p.variants[0] if p.variants else None
        result.append(WishlistItemResponse(
            id=item.id,
            product_id=p.id,
            created_at=item.created_at,
            product_name=p.name,
            product_brand=p.brand.name if p.brand else None,
            product_image=p.images[0] if p.images else None,
            product_price=variant.price if variant else None,
            product_compare_price=variant.compare_at_price if variant else None,
            product_slug=p.slug,
        ))
    return result


@router.post("/{product_id}", status_code=201)
async def add_to_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id,
    ).first()
    if existing:
        return {"message": "Ya está en favoritos"}
    item = Wishlist(user_id=current_user.id, product_id=product_id)
    db.add(item)
    db.commit()
    return {"message": "Agregado a favoritos"}


@router.delete("/{product_id}", status_code=204)
async def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id,
    ).first()
    if item:
        db.delete(item)
        db.commit()


@router.get("/check/{product_id}")
async def check_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id,
    ).first() is not None
    return {"is_favorited": exists}
