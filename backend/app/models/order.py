from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class ShippingMethod(str, enum.Enum):
    standard = "standard"
    express = "express"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    subtotal = Column(Float, nullable=False)
    shipping_cost = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    shipping_method = Column(Enum(ShippingMethod), default=ShippingMethod.standard)
    coupon_code = Column(String(50), nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    payment_method = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True)
    tracking_company = Column(String(100), nullable=True)
    tracking_url = Column(String(500), nullable=True)

    # Shipping address (denormalized for historical accuracy)
    shipping_email = Column(String(255), nullable=False)
    shipping_first_name = Column(String(100), nullable=False)
    shipping_last_name = Column(String(100), nullable=False)
    shipping_address = Column(String(255), nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    shipping_country = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    product_name = Column(String(255), nullable=False)   # snapshot
    size_ml = Column(Integer, nullable=False)             # snapshot
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(50), default="Casa")
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")
