from pydantic import BaseModel
from typing import List, Optional


class MessageResponse(BaseModel):
    message: str


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    product_count: int = 0
    model_config = {"from_attributes": True}


class BrandBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandResponse(BrandBase):
    id: int
    product_count: int = 0
    model_config = {"from_attributes": True}


class CouponBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    min_order_amount: float = 0.0
    max_uses: Optional[int] = None
    is_active: bool = True


class CouponCreate(CouponBase):
    pass


class CouponResponse(CouponBase):
    id: int
    used_count: int
    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    title: Optional[str] = None
    body: Optional[str] = None
    images: Optional[List[str]] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    title: Optional[str] = None
    body: Optional[str] = None
    images: Optional[List[str]] = None
    is_approved: bool
    user_name: Optional[str] = None
    model_config = {"from_attributes": True}
