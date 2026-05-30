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
