from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import Base, engine
from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.categories import (
    categories_router, brands_router, coupons_router, reviews_router, filters_router
)
from app.api.upload import router as upload_router
from app.api.reports import router as reports_router
from app.api.admin import router as admin_router
from app.api.addresses import router as addresses_router
from app.api.returns import router as returns_router
from app.api.contact import router as contact_router
from app.api.wishlist import router as wishlist_router
from app.api.loyalty import router as loyalty_router
from app.api.payments import router as payments_router
import app.models.wishlist  # ensure tables are created

# Create tables
Base.metadata.create_all(bind=engine)

# Create upload directory
os.makedirs(os.path.join(settings.UPLOAD_DIR, "products"), exist_ok=True)

app = FastAPI(
    title="Aroma-Distribuido API",
    description="Backend API para e-commerce de perfumería de lujo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded images
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(brands_router, prefix="/api/v1")
app.include_router(coupons_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
app.include_router(filters_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(addresses_router, prefix="/api/v1")
app.include_router(returns_router, prefix="/api/v1")
app.include_router(contact_router, prefix="/api/v1")
app.include_router(wishlist_router, prefix="/api/v1")
app.include_router(loyalty_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "Aroma-Distribuido API v1.0.0"}
