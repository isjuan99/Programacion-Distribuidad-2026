from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, or_, cast, String as SAString
from typing import Optional, List
import re

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.product import Product, ProductVariant, ProductStatus
from app.models.category import Review
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductListResponse, ProductVariantCreate
)

router = APIRouter(prefix="/products", tags=["products"])


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


def _enrich(product: Product, db: Session) -> dict:
    avg = db.query(func.avg(Review.rating)).filter(
        Review.product_id == product.id, Review.is_approved == True
    ).scalar()
    count = db.query(func.count(Review.id)).filter(
        Review.product_id == product.id, Review.is_approved == True
    ).scalar()
    d = {c.name: getattr(product, c.name) for c in product.__table__.columns}
    d["variants"] = product.variants
    d["brand_name"] = product.brand.name if product.brand else None
    d["category_name"] = product.category.name if product.category else None
    d["average_rating"] = round(float(avg), 1) if avg else None
    d["review_count"] = count or 0
    return d


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(9, ge=1, le=100),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    size_ml: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    featured: Optional[bool] = None,
    on_sale: Optional[bool] = None,
    gender: Optional[str] = None,
    category_names: Optional[str] = None,
    top_notes: Optional[str] = None,
    heart_notes: Optional[str] = None,
    base_notes: Optional[str] = None,
    sort: str = "created_at_desc",
    db: Session = Depends(get_db),
):
    query = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
        joinedload(Product.category),
    )
    if status:
        query = query.filter(Product.status == status)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if featured is not None:
        query = query.filter(Product.is_featured == featured)
    if gender:
        query = query.filter(Product.gender == gender)
    if category_names:
        from app.models.category import Category
        terms = [t.strip() for t in category_names.split(',') if t.strip()]
        cat_subq = (
            db.query(Category.id)
            .filter(or_(*[Category.name.ilike(f'%{t}%') for t in terms]))
            .subquery()
        )
        query = query.filter(Product.category_id.in_(cat_subq))
    if on_sale:
        sale_subq = (
            db.query(ProductVariant.product_id)
            .filter(
                ProductVariant.compare_at_price.isnot(None),
                ProductVariant.compare_at_price > ProductVariant.price,
            )
            .subquery()
        )
        query = query.filter(Product.id.in_(sale_subq))
    if search:
        query = query.filter(
            or_(Product.name.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%"))
        )
    if min_price or max_price or size_ml:
        variant_q = db.query(ProductVariant.product_id)
        if min_price:
            variant_q = variant_q.filter(ProductVariant.price >= min_price)
        if max_price:
            variant_q = variant_q.filter(ProductVariant.price <= max_price)
        if size_ml:
            variant_q = variant_q.filter(ProductVariant.size_ml == size_ml)
        query = query.filter(Product.id.in_(variant_q.subquery()))

    # Olfactory notes filter
    for notes_param in [top_notes, heart_notes, base_notes]:
        if notes_param:
            note_list = [n.strip().lower() for n in notes_param.split(',') if n.strip()]
            for note in note_list:
                query = query.filter(
                    cast(Product.olfactory_notes, SAString).ilike(f'%{note}%')
                )

    sort_map = {
        "created_at_desc": Product.created_at.desc(),
        "created_at_asc": Product.created_at.asc(),
        "name_asc": Product.name.asc(),
    }
    query = query.order_by(sort_map.get(sort, Product.created_at.desc()))
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    return ProductListResponse(
        items=[ProductResponse.model_validate(_enrich(p, db)) for p in products],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    if len(q) < 2:
        return []
    from app.models.category import Brand
    products = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
    ).filter(
        Product.status == ProductStatus.active,
        or_(
            Product.name.ilike(f"%{q}%"),
            cast(Product.olfactory_notes, SAString).ilike(f"%{q}%"),
        )
    ).limit(5).all()

    brand_matches = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
    ).join(Product.brand).filter(
        Product.status == ProductStatus.active,
        Brand.name.ilike(f"%{q}%"),
    ).limit(3).all()

    seen_ids = {p.id for p in products}
    for p in brand_matches:
        if p.id not in seen_ids:
            products.append(p)
            seen_ids.add(p.id)

    results = []
    for p in products[:5]:
        min_price = min((v.price for v in p.variants), default=None)
        results.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand.name if p.brand else None,
            "primary_image": p.images[0] if p.images else None,
            "price": min_price,
            "slug": p.slug,
        })
    return results


@router.get("/bundles", response_model=ProductListResponse)
async def list_bundles(
    page: int = Query(1, ge=1),
    per_page: int = Query(9),
    db: Session = Depends(get_db),
):
    query = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
        joinedload(Product.category),
    ).filter(Product.is_bundle == True, Product.status == ProductStatus.active)
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    return ProductListResponse(
        items=[ProductResponse.model_validate(_enrich(p, db)) for p in products],
        total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
        joinedload(Product.category),
    ).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductResponse.model_validate(_enrich(product, db))


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    slug = _slugify(data.name)
    base = slug
    n = 1
    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base}-{n}"
        n += 1
    product = Product(**data.model_dump(exclude={"variants"}), slug=slug)
    db.add(product)
    db.flush()
    for v in data.variants:
        variant = ProductVariant(**v.model_dump(), product_id=product.id)
        db.add(variant)
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(_enrich(product, db))


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    product = db.query(Product).options(
        selectinload(Product.variants)
    ).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = data.model_dump(exclude_none=True)
    variants_data = update_data.pop('variants', None)

    for field, value in update_data.items():
        setattr(product, field, value)

    if variants_data is not None:
        from app.models.order import OrderItem
        existing = {v.id: v for v in product.variants}
        updated_ids = set()

        for v_data in variants_data:
            v_id = v_data.pop('id', None)
            if v_id and v_id in existing:
                # Actualiza variante existente sin borrarla
                v = existing[v_id]
                for field, val in v_data.items():
                    setattr(v, field, val)
                updated_ids.add(v_id)
            else:
                # Crea variante nueva
                db.add(ProductVariant(**v_data, product_id=product.id))

        # Solo elimina variantes que no están en el update Y no tienen pedidos
        for v_id, v in existing.items():
            if v_id not in updated_ids:
                in_orders = db.query(func.count(OrderItem.id)).filter(
                    OrderItem.variant_id == v_id
                ).scalar()
                if in_orders == 0:
                    db.delete(v)

    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(_enrich(product, db))


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()


@router.get("/{product_id}/related", response_model=ProductListResponse)
async def get_related_products(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
        joinedload(Product.category),
    ).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    related: list = []
    seen_ids = {product_id}

    def _add(items):
        for p in items:
            if p.id not in seen_ids and len(related) < 8:
                related.append(p)
                seen_ids.add(p.id)

    base_q = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
        joinedload(Product.category),
    ).filter(
        Product.status == ProductStatus.active,
        Product.id != product_id,
    )

    _add(base_q.filter(Product.category_id == product.category_id).limit(4).all())

    if product.olfactory_notes and len(related) < 8:
        for note in (product.olfactory_notes or [])[:3]:
            note_matches = base_q.filter(
                cast(Product.olfactory_notes, SAString).ilike(f'%{note}%'),
                Product.id.notin_(list(seen_ids)),
            ).limit(2).all()
            _add(note_matches)

    if len(related) < 8:
        _add(base_q.filter(
            Product.brand_id == product.brand_id,
            Product.id.notin_(list(seen_ids)),
        ).limit(4).all())

    if len(related) < 4:
        _add(base_q.filter(
            Product.is_featured == True,
            Product.id.notin_(list(seen_ids)),
        ).limit(8 - len(related)).all())

    return ProductListResponse(
        items=[ProductResponse.model_validate(_enrich(p, db)) for p in related],
        total=len(related),
        page=1,
        per_page=8,
        pages=1,
    )


@router.get("/{product_id}/fragrance-profile")
async def get_fragrance_profile(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    notes = set(n.lower() for n in (product.olfactory_notes or []))
    if not notes:
        return []

    candidates = db.query(Product).options(
        selectinload(Product.variants),
        joinedload(Product.brand),
    ).filter(
        Product.status == ProductStatus.active,
        Product.id != product_id,
        Product.is_bundle == False,
    ).all()

    scored = []
    for p in candidates:
        p_notes = set(n.lower() for n in (p.olfactory_notes or []))
        if not p_notes:
            continue
        common = notes & p_notes
        if len(common) >= 1:
            match_pct = round(len(common) / max(len(notes), len(p_notes)) * 100)
            min_price = min((v.price for v in p.variants), default=None)
            scored.append({
                "id": p.id,
                "name": p.name,
                "brand": p.brand.name if p.brand else None,
                "primary_image": p.images[0] if p.images else None,
                "price": min_price,
                "slug": p.slug,
                "match_pct": match_pct,
                "common_notes": list(common),
            })

    scored.sort(key=lambda x: x["match_pct"], reverse=True)
    return scored[:4]
