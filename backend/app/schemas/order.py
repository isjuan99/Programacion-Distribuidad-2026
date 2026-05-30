from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus, ShippingMethod


class OrderItemCreate(BaseModel):
    variant_id: int
    quantity: int


class ShippingDetails(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    address: str
    city: str
    postal_code: str
    country: str


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping: ShippingDetails
    shipping_method: ShippingMethod = ShippingMethod.standard
    coupon_code: Optional[str] = None
    payment_method: str = "card"


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    variant_id: int
    product_name: str
    size_ml: int
    quantity: int
    unit_price: float
    total_price: float
    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: OrderStatus
    subtotal: float
    shipping_cost: float
    tax: float
    discount: float
    total: float
    shipping_method: ShippingMethod
    coupon_code: Optional[str] = None
    payment_method: Optional[str] = None
    shipping_email: str
    shipping_first_name: str
    shipping_last_name: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str
    created_at: datetime
    tracking_number: Optional[str] = None
    tracking_company: Optional[str] = None
    tracking_url: Optional[str] = None
    items: List[OrderItemResponse] = []
    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    per_page: int
    pages: int


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class TrackingUpdate(BaseModel):
    tracking_number: str
    tracking_company: str
    tracking_url: Optional[str] = None
