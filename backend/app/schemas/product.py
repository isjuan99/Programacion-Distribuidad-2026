from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductStatus


class ProductVariantBase(BaseModel):
    size_ml: int
    price: float
    compare_at_price: Optional[float] = None
    stock: int = 0
    sku: Optional[str] = None


class ProductVariantCreate(ProductVariantBase):
    id: Optional[int] = None


class ProductVariantResponse(ProductVariantBase):
    id: int
    product_id: int
    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name: str
    brand_id: int
    category_id: int
    description: Optional[str] = None
    olfactory_notes: List[str] = []
    images: List[str] = []
    status: ProductStatus = ProductStatus.draft
    is_featured: bool = False
    is_new: bool = False
    gender: Optional[str] = None  # 'hombre', 'mujer', 'unisex'


class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    olfactory_notes: Optional[List[str]] = None
    images: Optional[List[str]] = None
    status: Optional[ProductStatus] = None
    is_featured: Optional[bool] = None
    is_new: Optional[bool] = None
    gender: Optional[str] = None
    variants: Optional[List[ProductVariantCreate]] = None


class ProductResponse(ProductBase):
    id: int
    slug: str
    images: List[str] = []
    created_at: datetime
    variants: List[ProductVariantResponse] = []
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    average_rating: Optional[float] = None
    review_count: int = 0

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    per_page: int
    pages: int
