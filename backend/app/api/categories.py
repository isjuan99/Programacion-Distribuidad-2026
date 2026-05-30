from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.models.category import Category, Brand, Coupon, Review
from app.models.product import Product
from app.models.user import User
from app.schemas.common import (
    CategoryCreate, CategoryResponse,
    BrandCreate, BrandResponse,
    CouponCreate, CouponResponse,
    ReviewCreate, ReviewResponse,
    MessageResponse,
)

# ── Categories ────────────────────────────────────────────────────────────────
categories_router = APIRouter(prefix="/categories", tags=["categories"])


@categories_router.get("", response_model=List[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).filter(Category.is_active == True).all()
    result = []
    for c in cats:
        count = db.query(func.count(Product.id)).filter(Product.category_id == c.id).scalar()
        d = {col.name: getattr(c, col.name) for col in c.__table__.columns}
        d["product_count"] = count
        result.append(CategoryResponse.model_validate(d))
    return result


@categories_router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    d = {col.name: getattr(cat, col.name) for col in cat.__table__.columns}
    d["product_count"] = 0
    return CategoryResponse.model_validate(d)


@categories_router.delete("/{cat_id}", status_code=204)
async def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(cat)
    db.commit()


# ── Brands ────────────────────────────────────────────────────────────────────
brands_router = APIRouter(prefix="/brands", tags=["brands"])


@brands_router.get("", response_model=List[BrandResponse])
async def list_brands(db: Session = Depends(get_db)):
    brands = db.query(Brand).filter(Brand.is_active == True).all()
    result = []
    for b in brands:
        count = db.query(func.count(Product.id)).filter(Product.brand_id == b.id).scalar()
        d = {col.name: getattr(b, col.name) for col in b.__table__.columns}
        d["product_count"] = count
        result.append(BrandResponse.model_validate(d))
    return result


@brands_router.post("", response_model=BrandResponse, status_code=201)
async def create_brand(
    data: BrandCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    brand = Brand(**data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    d = {col.name: getattr(brand, col.name) for col in brand.__table__.columns}
    d["product_count"] = 0
    return BrandResponse.model_validate(d)


# ── Coupons ───────────────────────────────────────────────────────────────────
coupons_router = APIRouter(prefix="/coupons", tags=["coupons"])


@coupons_router.post("/validate", response_model=CouponResponse)
async def validate_coupon(code: str, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(
        Coupon.code == code.upper(), Coupon.is_active == True
    ).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupón inválido")
    return CouponResponse.model_validate(coupon)


@coupons_router.get("", response_model=List[CouponResponse])
async def list_coupons(
    db: Session = Depends(get_db), _: User = Depends(get_current_admin)
):
    return [CouponResponse.model_validate(c) for c in db.query(Coupon).all()]


@coupons_router.post("", response_model=CouponResponse, status_code=201)
async def create_coupon(
    data: CouponCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    coupon = Coupon(**data.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return CouponResponse.model_validate(coupon)


# ── Reviews ───────────────────────────────────────────────────────────────────
reviews_router = APIRouter(prefix="/reviews", tags=["reviews"])


@reviews_router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        Review.product_id == product_id, Review.is_approved == True
    ).all()
    return [
        ReviewResponse.model_validate({
            **{col.name: getattr(r, col.name) for col in r.__table__.columns},
            "user_name": f"{r.user.first_name} {r.user.last_name[0]}." if r.user else "Anónimo",
        })
        for r in reviews
    ]


@reviews_router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = Review(
        user_id=current_user.id,
        product_id=data.product_id,
        rating=data.rating,
        title=data.title,
        body=data.body,
        images=data.images or [],
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return ReviewResponse.model_validate({
        **{col.name: getattr(review, col.name) for col in review.__table__.columns},
        "user_name": f"{current_user.first_name} {current_user.last_name[0]}.",
    })


@reviews_router.patch("/{review_id}/approve", response_model=ReviewResponse)
async def approve_review(
    review_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    review.is_approved = True
    db.commit()
    return ReviewResponse.model_validate({
        **{col.name: getattr(review, col.name) for col in review.__table__.columns},
        "user_name": None,
    })


# ── Filters ───────────────────────────────────────────────────────────────────
filters_router = APIRouter(prefix="/filters", tags=["filters"])


@filters_router.get("/olfactory-notes")
async def get_olfactory_notes(db: Session = Depends(get_db)):
    from app.models.product import Product, ProductStatus
    from sqlalchemy import cast, String as SAString
    products = db.query(Product.olfactory_notes).filter(
        Product.status == ProductStatus.active,
        Product.olfactory_notes.isnot(None),
    ).all()
    all_notes = set()
    for (notes,) in products:
        if isinstance(notes, list):
            for note in notes:
                if note:
                    all_notes.add(note.lower().strip())
    return sorted(list(all_notes))
