import sys
import os
sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.order import Order, OrderItem, Address
from app.models.product import Product, ProductVariant
from app.models.category import Category, Brand, Coupon, Review
from app.models.user import User

def create_admin(email: str, password: str, first_name: str, last_name: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.commit()
                print(f"Usuario existente '{email}' actualizado a admin.")
            else:
                print(f"El usuario '{email}' ya es admin.")
            return

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_admin=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        print(f"Admin creado exitosamente: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    email     = sys.argv[1] if len(sys.argv) > 1 else "admin@aroma.com"
    password  = sys.argv[2] if len(sys.argv) > 2 else "Admin1234"
    first     = sys.argv[3] if len(sys.argv) > 3 else "Admin"
    last      = sys.argv[4] if len(sys.argv) > 4 else "Aroma"
    create_admin(email, password, first, last)
