from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    loyalty_points = Column(Integer, default=0)
    avatar_url = Column(String(500), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    verification_token = Column(String(255), nullable=True)
    google_id = Column(String(255), nullable=True, index=True)
    apple_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    addresses = relationship("Address", back_populates="user")
