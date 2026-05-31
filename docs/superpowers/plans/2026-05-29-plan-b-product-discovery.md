# Plan B — Product & Discovery Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement search autocomplete (Feature 11), related products with recommendation logic (Feature 12), review photos (Feature 14), gift bundles/sets (Feature 15), olfactory notes filter in shop (Feature 16), and fragrance profile recommendations (Feature 17).

**Architecture:** Backend gets new endpoints added to `products.py` and `categories.py` (reviews), plus new models for bundles. Frontend gets a new `SearchAutocomplete.vue` component, updated `ShopPage.vue` filter sidebar, updated `ProductPage.vue` for related/recommendations/review-photos, and updated admin product form for bundles.

**Tech Stack:** FastAPI, SQLAlchemy (JSON array filtering via `cast`), Vue 3 Composition API, Pinia, Tailwind CSS, Swiper.js (already installed), vue-i18n

---

## File Map

**New backend files:**
- `backend/alembic/versions/002_product_features.py` — migration for bundles, review images

**Modified backend files:**
- `backend/app/models/product.py` — add `is_bundle` field, add `BundleItem` model
- `backend/app/models/category.py` — add `images` JSON field to Review
- `backend/app/api/products.py` — add `/suggestions`, `/{id}/related`, `/bundles`, `/fragrance-profile` endpoints; add olfactory_notes filter to list endpoint
- `backend/app/api/categories.py` — update reviews POST to accept images; add `/filters/olfactory-notes` endpoint
- `backend/app/schemas/product.py` — add BundleItemCreate, BundleItemResponse; update ProductCreate for bundles
- `backend/app/schemas/common.py` — add SuggestionResponse

**New frontend files:**
- `frontend/src/components/ui/SearchAutocomplete.vue`

**Modified frontend files:**
- `frontend/src/pages/ShopPage.vue` — add olfactory notes filter section
- `frontend/src/pages/ProductPage.vue` — update related products, add fragrance profile section, review photos
- `frontend/src/pages/admin/AdminProducts.vue` — add bundle fields to product form
- `frontend/src/components/layout/Header.vue` — replace plain search with SearchAutocomplete
- `frontend/src/locales/es.json` — new keys
- `frontend/src/locales/en.json` — new keys

---

## Task 1: Migration — Bundle Items & Review Images

**Files:**
- Create: `backend/alembic/versions/002_product_features.py`

- [ ] **Step 1: Create migration**

```python
"""add bundle_items table and review images field

Revision ID: 002_product_features
Revises: 001_auth_user
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_product_features'
down_revision = '001_auth_user'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('is_bundle', sa.Boolean(), nullable=True, server_default='false'))
    op.create_table(
        'bundle_items',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('bundle_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('product_variants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
    )
    op.add_column('reviews', sa.Column('images', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('reviews', 'images')
    op.drop_table('bundle_items')
    op.drop_column('products', 'is_bundle')
```

- [ ] **Step 2: Run migration**

```bash
cd backend
alembic upgrade head
```

Expected: `Running upgrade 001_auth_user -> 002_product_features`

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/002_product_features.py
git commit -m "feat: migration — bundle_items table, review images field, is_bundle on products"
```

---

## Task 2: Update Product Model — Bundles

**Files:**
- Modify: `backend/app/models/product.py`

- [ ] **Step 1: Add is_bundle field and BundleItem model**

Replace the entire `backend/app/models/product.py`:

```python
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ProductStatus(str, enum.Enum):
    active = "active"
    draft = "draft"
    out_of_stock = "out_of_stock"
    discontinued = "discontinued"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    olfactory_notes = Column(JSON, default=list)
    status = Column(Enum(ProductStatus), default=ProductStatus.draft)
    is_featured = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)
    is_bundle = Column(Boolean, default=False)
    images = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    bundle_items = relationship("BundleItem", foreign_keys="BundleItem.bundle_id", back_populates="bundle", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    size_ml = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    sku = Column(String(100), unique=True, index=True)

    product = relationship("Product", back_populates="variants")


class BundleItem(Base):
    __tablename__ = "bundle_items"

    id = Column(Integer, primary_key=True, index=True)
    bundle_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)

    bundle = relationship("Product", foreign_keys=[bundle_id], back_populates="bundle_items")
    product = relationship("Product", foreign_keys=[product_id])
    variant = relationship("ProductVariant")
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/product.py
git commit -m "feat: add is_bundle field and BundleItem model to product"
```

---

## Task 3: Update Review Model

**Files:**
- Modify: `backend/app/models/category.py`

- [ ] **Step 1: Add images field to Review**

In `backend/app/models/category.py`, replace the Review class:

```python
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)   # 1–5
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    images = Column(JSON, default=list)        # list of image URLs
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
```

Also add the JSON import if not present at top: `from sqlalchemy import ... JSON ...`

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/category.py
git commit -m "feat: add images JSON field to Review model"
```

---

## Task 4: Backend — Search Autocomplete & Olfactory Filter Endpoints

**Files:**
- Modify: `backend/app/api/products.py`

- [ ] **Step 1: Add suggestions, related, olfactory-filter endpoints to products.py**

Add the following imports at the top of `backend/app/api/products.py`:

```python
from sqlalchemy import cast, String as SAString
```

Add olfactory_notes filter parameters to `list_products`:

```python
# Add to list_products signature:
    top_notes: Optional[str] = None,      # comma-separated
    heart_notes: Optional[str] = None,
    base_notes: Optional[str] = None,
```

Add this filtering block inside `list_products`, after the `search` filter and before sort:

```python
    # Olfactory notes filter (JSON array contains any of the given notes)
    for notes_param in [top_notes, heart_notes, base_notes]:
        if notes_param:
            note_list = [n.strip().lower() for n in notes_param.split(',') if n.strip()]
            for note in note_list:
                query = query.filter(
                    cast(Product.olfactory_notes, SAString).ilike(f'%{note}%')
                )
```

Add these new endpoints at the bottom of `backend/app/api/products.py`:

```python

@router.get("/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    """Return up to 5 product suggestions for autocomplete."""
    if len(q) < 2:
        return []
    from sqlalchemy import or_
    products = db.query(Product).options(
        joinedload(Product.variants),
        joinedload(Product.brand),
    ).filter(
        Product.status == ProductStatus.active,
        or_(
            Product.name.ilike(f"%{q}%"),
            cast(Product.olfactory_notes, SAString).ilike(f"%{q}%"),
        )
    ).limit(5).all()

    # Also search by brand name
    from app.models.category import Brand
    brand_matches = db.query(Product).options(
        joinedload(Product.variants),
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


@router.get("/{product_id}/related", response_model=ProductListResponse)
async def get_related_products(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Return up to 8 related products based on category > notes > brand > price."""
    product = db.query(Product).options(
        joinedload(Product.variants),
        joinedload(Product.brand),
        joinedload(Product.category),
    ).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    related: list[Product] = []
    seen_ids = {product_id}

    def _add(items):
        for p in items:
            if p.id not in seen_ids and len(related) < 8:
                related.append(p)
                seen_ids.add(p.id)

    base_q = db.query(Product).options(
        joinedload(Product.variants),
        joinedload(Product.brand),
        joinedload(Product.category),
    ).filter(
        Product.status == ProductStatus.active,
        Product.id != product_id,
    )

    # Priority 1: same category
    _add(base_q.filter(Product.category_id == product.category_id).limit(4).all())

    # Priority 2: shared olfactory notes
    if product.olfactory_notes and len(related) < 8:
        for note in (product.olfactory_notes or [])[:3]:
            note_matches = base_q.filter(
                cast(Product.olfactory_notes, SAString).ilike(f'%{note}%'),
                Product.id.notin_(seen_ids),
            ).limit(2).all()
            _add(note_matches)

    # Priority 3: same brand
    if len(related) < 8:
        _add(base_q.filter(
            Product.brand_id == product.brand_id,
            Product.id.notin_(seen_ids),
        ).limit(4).all())

    # Priority 4: featured products as fallback
    if len(related) < 4:
        _add(base_q.filter(
            Product.is_featured == True,
            Product.id.notin_(seen_ids),
        ).limit(8 - len(related)).all())

    return ProductListResponse(
        items=[ProductResponse.model_validate(_enrich(p, db)) for p in related],
        total=len(related),
        page=1,
        per_page=8,
        pages=1,
    )


@router.get("/bundles", response_model=ProductListResponse)
async def list_bundles(
    page: int = Query(1, ge=1),
    per_page: int = Query(9),
    db: Session = Depends(get_db),
):
    query = db.query(Product).options(
        joinedload(Product.variants),
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


@router.get("/{product_id}/fragrance-profile")
async def get_fragrance_profile(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Return products with similar olfactory notes, with a match percentage."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    notes = set(n.lower() for n in (product.olfactory_notes or []))
    if not notes:
        return []

    candidates = db.query(Product).options(
        joinedload(Product.variants),
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/products.py
git commit -m "feat: search suggestions, related products, bundles, fragrance-profile, olfactory notes filter"
```

---

## Task 5: Backend — Olfactory Notes Filter List & Review Images

**Files:**
- Modify: `backend/app/api/categories.py`

- [ ] **Step 1: Add /filters/olfactory-notes endpoint and update review creation**

Add a new router for filters and update the reviews router. Add to `backend/app/api/categories.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy import cast, String as SAString, func
from typing import Optional, List
import json

# Add this router at the bottom of the file:
filters_router = APIRouter(prefix="/filters", tags=["filters"])

@filters_router.get("/olfactory-notes")
async def get_olfactory_notes(db: Session = Depends(get_db)):
    """Return all distinct olfactory notes present in active products."""
    from app.models.product import Product, ProductStatus
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
```

For the reviews POST endpoint, update to accept an optional `images` field (JSON string of URLs):

Find the existing `create_review` endpoint and update its signature and body:

```python
@reviews_router.post("/reviews", status_code=201)
async def create_review(
    product_id: int = Form(...),
    rating: int = Form(..., ge=1, le=5),
    title: Optional[str] = Form(None),
    body: Optional[str] = Form(None),
    images: Optional[str] = Form(None),  # JSON array of already-uploaded URLs
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id == product_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya dejaste una reseña para este producto")
    image_list = json.loads(images) if images else []
    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=rating,
        title=title,
        body=body,
        images=image_list,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
```

Also register `filters_router` in `backend/app/main.py`:

```python
from app.api.categories import categories_router, brands_router, coupons_router, reviews_router, filters_router
# ...
app.include_router(filters_router, prefix="/api/v1")
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/categories.py backend/app/main.py
git commit -m "feat: /filters/olfactory-notes endpoint, update reviews to accept images"
```

---

## Task 6: Frontend — SearchAutocomplete Component

**Files:**
- Create: `frontend/src/components/ui/SearchAutocomplete.vue`

- [ ] **Step 1: Create SearchAutocomplete.vue**

```vue
<template>
  <div class="relative" ref="containerRef">
    <div class="flex items-center border-b border-gray-700 focus-within:border-[#c9a84c] transition-colors">
      <svg class="w-4 h-4 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        :placeholder="$t('nav.search')"
        class="w-full bg-transparent text-white text-sm px-3 py-2 focus:outline-none placeholder-gray-600"
        @keydown.down.prevent="moveCursor(1)"
        @keydown.up.prevent="moveCursor(-1)"
        @keydown.enter.prevent="selectCurrent"
        @keydown.escape="close"
        @input="onInput"
      />
      <button v-if="query" @click="query = ''; suggestions = []" class="text-gray-500 hover:text-white shrink-0">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Dropdown -->
    <div
      v-if="showDropdown"
      class="absolute top-full left-0 right-0 mt-1 bg-[#111] border border-gray-800 shadow-2xl z-50 max-h-80 overflow-y-auto"
    >
      <!-- Loading -->
      <div v-if="loading" class="p-4 text-center text-gray-500 text-sm">
        <div class="w-4 h-4 mx-auto border border-[#c9a84c] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Results -->
      <template v-else-if="suggestions.length > 0">
        <RouterLink
          v-for="(s, i) in suggestions"
          :key="s.id"
          :to="`/product/${s.id}`"
          @click="close"
          class="flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors border-b border-gray-800/50 last:border-0"
          :class="{ 'bg-white/5': cursor === i }"
        >
          <img
            v-if="s.primary_image"
            :src="s.primary_image"
            :alt="s.name"
            class="w-10 h-10 object-cover shrink-0 bg-gray-800"
          />
          <div v-else class="w-10 h-10 bg-gray-800 shrink-0"></div>
          <div class="flex-1 min-w-0">
            <p class="text-white text-sm truncate">{{ s.name }}</p>
            <p class="text-gray-500 text-xs">{{ s.brand }}</p>
          </div>
          <span v-if="s.price" class="text-[#c9a84c] text-sm shrink-0">${{ s.price }}</span>
        </RouterLink>

        <!-- View all -->
        <RouterLink
          :to="`/shop?q=${encodeURIComponent(query)}`"
          @click="close"
          class="flex items-center justify-between px-4 py-3 text-sm text-[#c9a84c] hover:bg-white/5 transition-colors"
        >
          <span>{{ $t('search.view_all_results', { q: query }) }}</span>
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </RouterLink>
      </template>

      <!-- No results -->
      <div v-else class="px-4 py-4 text-sm text-gray-500 text-center">
        {{ $t('search.no_suggestions', { q: query }) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../router/api'

const router = useRouter()
const query = ref('')
const suggestions = ref([])
const loading = ref(false)
const cursor = ref(-1)
const containerRef = ref(null)
const inputRef = ref(null)
let debounceTimer = null

const showDropdown = computed(() => query.value.length >= 2 && (loading.value || suggestions.value.length > 0 || !loading.value))

function onInput() {
  cursor.value = -1
  clearTimeout(debounceTimer)
  if (query.value.length < 2) {
    suggestions.value = []
    return
  }
  loading.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const { data } = await api.get(`/products/suggestions?q=${encodeURIComponent(query.value)}`)
      suggestions.value = data
    } catch {
      suggestions.value = []
    } finally {
      loading.value = false
    }
  }, 300)
}

function moveCursor(dir) {
  const max = suggestions.value.length
  cursor.value = Math.max(-1, Math.min(max - 1, cursor.value + dir))
}

function selectCurrent() {
  if (cursor.value >= 0 && suggestions.value[cursor.value]) {
    router.push(`/product/${suggestions.value[cursor.value].id}`)
    close()
  } else if (query.value) {
    router.push(`/shop?q=${encodeURIComponent(query.value)}`)
    close()
  }
}

function close() {
  suggestions.value = []
  query.value = ''
  cursor.value = -1
}

function handleOutsideClick(e) {
  if (containerRef.value && !containerRef.value.contains(e.target)) {
    suggestions.value = []
  }
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))
</script>
```

- [ ] **Step 2: Replace search input in Header.vue with SearchAutocomplete**

In `frontend/src/components/layout/Header.vue`, find the existing search input/icon and replace it with:

```vue
<script setup>
import SearchAutocomplete from '../ui/SearchAutocomplete.vue'
</script>

<!-- Replace the existing search element with: -->
<div class="hidden md:block w-56 lg:w-72">
  <SearchAutocomplete />
</div>
```

- [ ] **Step 3: Also handle `?q=` query param in ShopPage**

In `frontend/src/pages/ShopPage.vue`, in `onMounted` or in the filters initialization, read `route.query.q` and set the search filter:

```javascript
import { useRoute } from 'vue-router'
const route = useRoute()

onMounted(() => {
  if (route.query.q) {
    filters.search = route.query.q
  }
  loadProducts()
})
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ui/SearchAutocomplete.vue frontend/src/components/layout/Header.vue frontend/src/pages/ShopPage.vue
git commit -m "feat: SearchAutocomplete component with debounce, keyboard nav, integrated in Header"
```

---

## Task 7: Frontend — Olfactory Notes Filter in Shop

**Files:**
- Modify: `frontend/src/pages/ShopPage.vue`

- [ ] **Step 1: Add olfactory notes filter state and fetch**

In the `<script setup>` of ShopPage.vue, add:

```javascript
const availableNotes = ref([])
const selectedNotes = ref([])

async function loadOlfactoryNotes() {
  try {
    const { data } = await api.get('/filters/olfactory-notes')
    availableNotes.value = data
  } catch { /* ignore */ }
}

// In onMounted, also call:
loadOlfactoryNotes()

// In the loadProducts function, add notes to params:
function buildParams() {
  return {
    page: currentPage.value,
    per_page: perPage.value,
    category_id: filters.category_id || undefined,
    brand_id: filters.brand_id || undefined,
    min_price: filters.min_price || undefined,
    max_price: filters.max_price || undefined,
    size_ml: filters.size_ml || undefined,
    search: filters.search || undefined,
    // Pass all selected notes as comma-separated in top_notes param
    // (simplified: no top/heart/base grouping — all notes in one param)
    top_notes: selectedNotes.value.length ? selectedNotes.value.join(',') : undefined,
  }
}

function toggleNote(note) {
  const idx = selectedNotes.value.indexOf(note)
  if (idx >= 0) selectedNotes.value.splice(idx, 1)
  else selectedNotes.value.push(note)
  loadProducts()
}

function removeNote(note) {
  selectedNotes.value = selectedNotes.value.filter(n => n !== note)
  loadProducts()
}
```

- [ ] **Step 2: Add olfactory filter UI to sidebar**

In the filter sidebar template of ShopPage.vue, add after the existing size filter:

```vue
<!-- Olfactory Notes Filter -->
<div class="border-t border-gray-800 pt-5">
  <h3 class="text-xs tracking-widest text-gray-400 uppercase mb-3">{{ $t('shop.olfactory_notes') }}</h3>
  
  <!-- Selected notes as removable tags -->
  <div v-if="selectedNotes.length" class="flex flex-wrap gap-2 mb-3">
    <button
      v-for="note in selectedNotes"
      :key="note"
      @click="removeNote(note)"
      class="flex items-center gap-1 bg-[#c9a84c]/20 text-[#c9a84c] text-xs px-2 py-1 border border-[#c9a84c]/30 hover:bg-[#c9a84c]/30 transition-colors"
    >
      {{ note }}
      <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>

  <!-- Available notes checkboxes (max 12 shown) -->
  <div class="space-y-1 max-h-48 overflow-y-auto pr-1">
    <label
      v-for="note in availableNotes.slice(0, 15)"
      :key="note"
      class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer hover:text-white transition-colors py-0.5"
    >
      <input
        type="checkbox"
        :checked="selectedNotes.includes(note)"
        @change="toggleNote(note)"
        class="accent-[#c9a84c] rounded"
      />
      <span class="capitalize">{{ note }}</span>
    </label>
  </div>
</div>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/ShopPage.vue
git commit -m "feat: olfactory notes filter in shop sidebar with removable tags"
```

---

## Task 8: Frontend — Related Products & Fragrance Profile on ProductPage

**Files:**
- Modify: `frontend/src/pages/ProductPage.vue`

- [ ] **Step 1: Add related products and fragrance profile data fetching**

In `ProductPage.vue` `<script setup>`, add:

```javascript
const relatedProducts = ref([])
const fragranceProfile = ref([])

async function loadRelated(productId) {
  try {
    const { data } = await api.get(`/products/${productId}/related`)
    relatedProducts.value = data.items || []
  } catch { /* ignore */ }
}

async function loadFragranceProfile(productId) {
  try {
    const { data } = await api.get(`/products/${productId}/fragrance-profile`)
    fragranceProfile.value = data || []
  } catch { /* ignore */ }
}

// Call these after loading the main product:
watch(() => route.params.id, async (id) => {
  await loadProduct(id)
  await Promise.all([loadRelated(id), loadFragranceProfile(id)])
}, { immediate: true })
```

- [ ] **Step 2: Add related products carousel template**

Replace/update the related products section in ProductPage.vue template:

```vue
<!-- Related Products -->
<section v-if="relatedProducts.length > 0" class="mt-16 border-t border-gray-800 pt-12">
  <h2 class="text-xl tracking-widest text-white uppercase mb-8">{{ $t('product.related_products') }}</h2>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <div
      v-for="p in relatedProducts.slice(0, 4)"
      :key="p.id"
      class="group cursor-pointer"
    >
      <RouterLink :to="`/product/${p.id}`">
        <div class="aspect-square overflow-hidden bg-gray-900 mb-3">
          <img
            v-if="p.images && p.images[0]"
            :src="p.images[0]"
            :alt="p.name"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-700">
            <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mb-1">{{ p.brand_name }}</p>
        <p class="text-sm text-white group-hover:text-[#c9a84c] transition-colors">{{ p.name }}</p>
        <p v-if="p.variants && p.variants[0]" class="text-[#c9a84c] text-sm mt-1">${{ p.variants[0].price }}</p>
      </RouterLink>
    </div>
  </div>
</section>

<!-- Fragrance Profile Recommendations -->
<section v-if="fragranceProfile.length > 0" class="mt-12 border-t border-gray-800 pt-12">
  <h2 class="text-xl tracking-widest text-white uppercase mb-2">{{ $t('product.if_you_like') }}</h2>
  <p class="text-sm text-gray-500 mb-8">{{ $t('product.fragrance_match_subtitle', { name: product?.name }) }}</p>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <div
      v-for="p in fragranceProfile"
      :key="p.id"
      class="group relative cursor-pointer"
    >
      <RouterLink :to="`/product/${p.id}`">
        <!-- Match badge -->
        <div class="absolute top-2 left-2 z-10 bg-[#c9a84c] text-black text-xs px-2 py-0.5 font-bold">
          {{ p.match_pct }}% match
        </div>
        <div class="aspect-square overflow-hidden bg-gray-900 mb-3">
          <img
            v-if="p.primary_image"
            :src="p.primary_image"
            :alt="p.name"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div v-else class="w-full h-full bg-gray-800"></div>
        </div>
        <p class="text-xs text-gray-500 mb-1">{{ p.brand }}</p>
        <p class="text-sm text-white group-hover:text-[#c9a84c] transition-colors">{{ p.name }}</p>
        <p v-if="p.price" class="text-[#c9a84c] text-sm mt-1">${{ p.price }}</p>
        <p v-if="p.common_notes?.length" class="text-xs text-gray-600 mt-1 capitalize">
          {{ p.common_notes.slice(0, 2).join(' · ') }}
        </p>
      </RouterLink>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/ProductPage.vue
git commit -m "feat: related products and fragrance profile sections on product detail page"
```

---

## Task 9: Frontend — Review Photos

**Files:**
- Modify: `frontend/src/pages/ProductPage.vue`

- [ ] **Step 1: Add review photo upload state**

In `ProductPage.vue` `<script setup>`, add:

```javascript
const reviewImages = ref([])  // array of { file, preview, url }
const lightboxImage = ref(null)

async function handleReviewImageUpload(event) {
  const files = Array.from(event.target.files)
  for (const file of files) {
    if (reviewImages.value.length >= 3) break
    if (file.size > 2 * 1024 * 1024) {
      alert(t('product.review_image_too_large'))
      continue
    }
    // Upload immediately
    const formData = new FormData()
    formData.append('file', file)
    try {
      const { data } = await api.post('/upload/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const preview = URL.createObjectURL(file)
      reviewImages.value.push({ preview, url: data.url })
    } catch {
      alert(t('product.review_image_upload_error'))
    }
  }
}

function removeReviewImage(index) {
  URL.revokeObjectURL(reviewImages.value[index].preview)
  reviewImages.value.splice(index, 1)
}

// Update submitReview to include images:
async function submitReview() {
  const formData = new FormData()
  formData.append('product_id', product.value.id)
  formData.append('rating', reviewForm.rating)
  if (reviewForm.title) formData.append('title', reviewForm.title)
  if (reviewForm.body) formData.append('body', reviewForm.body)
  if (reviewImages.value.length) {
    formData.append('images', JSON.stringify(reviewImages.value.map(i => i.url)))
  }
  await api.post('/reviews', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  reviewImages.value = []
  // ... rest of existing submit logic
}
```

- [ ] **Step 2: Add photo upload section to review form template**

In the review form section of ProductPage.vue, add after the body textarea and before the submit button:

```vue
<!-- Photo upload -->
<div>
  <p class="text-xs tracking-widest text-gray-400 mb-3">{{ $t('product.add_review_photos') }}</p>
  <div class="flex gap-3 flex-wrap">
    <!-- Uploaded previews -->
    <div
      v-for="(img, i) in reviewImages"
      :key="i"
      class="relative w-20 h-20 group"
    >
      <img :src="img.preview" class="w-full h-full object-cover border border-gray-700"/>
      <button
        type="button"
        @click="removeReviewImage(i)"
        class="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
      >×</button>
    </div>
    <!-- Add button (max 3) -->
    <label
      v-if="reviewImages.length < 3"
      class="w-20 h-20 border-2 border-dashed border-gray-700 hover:border-[#c9a84c] flex flex-col items-center justify-center text-gray-500 hover:text-[#c9a84c] cursor-pointer transition-colors"
    >
      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"/>
      </svg>
      <span class="text-xs mt-1">{{ $t('product.add_photo') }}</span>
      <input type="file" accept="image/jpeg,image/png,image/webp" multiple class="hidden" @change="handleReviewImageUpload"/>
    </label>
  </div>
  <p class="text-xs text-gray-600 mt-2">{{ $t('product.review_photo_hint') }}</p>
</div>
```

- [ ] **Step 3: Display review photos in published reviews**

In the reviews display loop, add after the review body text:

```vue
<!-- Review images -->
<div v-if="review.images && review.images.length" class="flex gap-2 mt-3 flex-wrap">
  <img
    v-for="(imgUrl, i) in review.images"
    :key="i"
    :src="imgUrl"
    :alt="`Foto de reseña ${i+1}`"
    class="w-16 h-16 object-cover border border-gray-800 cursor-pointer hover:border-[#c9a84c] transition-colors"
    @click="lightboxImage = imgUrl"
  />
</div>

<!-- Lightbox -->
<div
  v-if="lightboxImage"
  class="fixed inset-0 bg-black/90 flex items-center justify-center z-50"
  @click="lightboxImage = null"
>
  <img :src="lightboxImage" class="max-w-full max-h-full object-contain" @click.stop/>
  <button @click="lightboxImage = null" class="absolute top-4 right-4 text-white hover:text-[#c9a84c]">
    <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
    </svg>
  </button>
</div>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/ProductPage.vue
git commit -m "feat: review photos upload (max 3), lightbox display in published reviews"
```

---

## Task 10: Frontend — Bundle Product Display

**Files:**
- Modify: `frontend/src/pages/ProductPage.vue`
- Modify: `frontend/src/pages/admin/AdminProducts.vue`

- [ ] **Step 1: Add bundle info display on product page**

In ProductPage.vue, add a bundle info section after the product description (only shown when `product.is_bundle` is true). First, fetch bundle items separately:

```javascript
const bundleItems = ref([])

async function loadBundleItems(productId) {
  // Bundle items are included in the product data when is_bundle=true
  // They come via a new field on ProductResponse
  // For now, display is_bundle badge and description only
}
```

Add to the product info section in the template:

```vue
<!-- Bundle badge and content list -->
<div v-if="product?.is_bundle" class="border border-[#c9a84c]/30 bg-[#c9a84c]/5 p-4 mt-4">
  <div class="flex items-center gap-2 mb-3">
    <span class="text-xs bg-[#c9a84c] text-black px-2 py-0.5 tracking-widest font-bold">GIFT SET</span>
    <span class="text-sm text-[#c9a84c]">{{ $t('product.bundle_label') }}</span>
  </div>
  <p class="text-sm text-gray-400">{{ $t('product.bundle_includes') }}</p>
</div>
```

- [ ] **Step 2: Add bundle toggle to admin product form**

In `frontend/src/pages/admin/AdminProducts.vue`, in the product create/edit form, add:

```vue
<!-- Bundle toggle -->
<div class="flex items-center gap-3">
  <label class="flex items-center gap-2 cursor-pointer">
    <input type="checkbox" v-model="productForm.is_bundle" class="accent-[#c9a84c] w-4 h-4"/>
    <span class="text-sm text-gray-300">{{ $t('admin.is_bundle') }}</span>
  </label>
  <span class="text-xs text-gray-500">{{ $t('admin.bundle_hint') }}</span>
</div>
```

Also ensure `is_bundle` is included in `productForm` initial state and in the submit payload.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/ProductPage.vue frontend/src/pages/admin/AdminProducts.vue
git commit -m "feat: bundle/gift-set badge on product page, bundle toggle in admin product form"
```

---

## Task 11: i18n Translations — Product & Discovery

**Files:**
- Modify: `frontend/src/locales/es.json`
- Modify: `frontend/src/locales/en.json`

- [ ] **Step 1: Add Spanish keys**

Add under `"shop"`:
```json
"olfactory_notes": "Notas Olfativas",
"clear_notes": "Limpiar notas"
```

Add under `"product"`:
```json
"if_you_like": "Si te gusta, también prueba",
"fragrance_match_subtitle": "Fragancias con notas similares a {name}",
"bundle_label": "Set de Regalo",
"bundle_includes": "Este set incluye varios productos seleccionados",
"add_review_photos": "Agrega fotos de tu compra (opcional)",
"add_photo": "Agregar",
"review_photo_hint": "Máx. 3 fotos · JPG, PNG, WEBP · 2MB c/u",
"review_image_too_large": "La imagen supera 2MB",
"review_image_upload_error": "Error al subir la imagen"
```

Add under `"search"` (new section):
```json
"view_all_results": "Ver todos los resultados para \"{q}\"",
"no_suggestions": "Sin resultados para \"{q}\""
```

Add under `"admin"`:
```json
"is_bundle": "¿Es un set/bundle?",
"bundle_hint": "Los bundles agrupan varios productos en una oferta especial"
```

- [ ] **Step 2: Add English keys**

Same sections in `en.json`:

Under `"shop"`:
```json
"olfactory_notes": "Olfactory Notes",
"clear_notes": "Clear notes"
```

Under `"product"`:
```json
"if_you_like": "If you like this, also try",
"fragrance_match_subtitle": "Fragrances with similar notes to {name}",
"bundle_label": "Gift Set",
"bundle_includes": "This set includes several curated products",
"add_review_photos": "Add photos of your purchase (optional)",
"add_photo": "Add",
"review_photo_hint": "Max 3 photos · JPG, PNG, WEBP · 2MB each",
"review_image_too_large": "Image exceeds 2MB",
"review_image_upload_error": "Error uploading image"
```

Under `"search"`:
```json
"view_all_results": "View all results for \"{q}\"",
"no_suggestions": "No results for \"{q}\""
```

Under `"admin"`:
```json
"is_bundle": "Is this a bundle/gift set?",
"bundle_hint": "Bundles group multiple products in a special offer"
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/locales/es.json frontend/src/locales/en.json
git commit -m "feat: i18n translations for search, olfactory filter, bundles, review photos, fragrance profile"
```

---

## Verification

- [ ] Type "rose" in header search → dropdown shows matching products with images, price, brand
- [ ] Press arrow keys → cursor moves; Enter → navigates to product
- [ ] Click "Ver todos los resultados" → navigates to /shop?q=rose
- [ ] In /shop sidebar → "Notas Olfativas" section shows available notes
- [ ] Select "bergamota" → products filter; tag appears with × to remove
- [ ] Product detail page → "También te puede interesar" shows up to 4 related items
- [ ] "Si te gusta X, prueba estos" section shows match % badges
- [ ] Review form → can upload up to 3 images, preview shows, × removes them
- [ ] Published review with images → thumbnails shown; click opens lightbox
- [ ] Admin product form → bundle checkbox available; saved correctly
