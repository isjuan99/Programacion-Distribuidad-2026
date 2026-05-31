from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
import os
import logging

from app.middleware.logging_setup import setup_logging
setup_logging()

from app.core.config import settings
from app.core.database import Base, engine
from app.core.redis_client import get_redis, close_redis
from app.core.rabbitmq import get_rabbitmq_channel, close_rabbitmq, check_rabbitmq_health
from app.core.redis_client import check_redis_health
from app.middleware.request_id import RequestIDMiddleware
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
from app.api.simulate import router as simulate_router
import app.models.wishlist

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Aroma-Distribuido backend", extra={"event": "startup"})
    Base.metadata.create_all(bind=engine)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "products"), exist_ok=True)
    await get_redis()
    await get_rabbitmq_channel()
    yield
    logger.info("Shutting down Aroma-Distribuido backend", extra={"event": "shutdown"})
    await close_redis()
    await close_rabbitmq()


app = FastAPI(
    title="Aroma-Distribuido API",
    description="""
## API de E-Commerce de Perfumería de Lujo — Sistema Distribuido

Plataforma completa con arquitectura distribuida que incluye:

- **Redis**: Caché de productos, categorías y búsquedas
- **RabbitMQ**: Mensajería de eventos (pedidos, usuarios, inventario)
- **Worker**: Procesamiento asíncrono de notificaciones y tareas
- **Logs estructurados**: JSON logging con Request-ID por solicitud
- **Observabilidad**: Health checks, métricas y simulación de fallos

### Autenticación
Usa JWT Bearer tokens. Obtén tu token en `/api/v1/auth/login`.

### Request ID
Cada respuesta incluye el header `X-Request-ID` para trazabilidad.
""",
    version="2.0.0",
    contact={"name": "Aroma-Distribuido", "email": "aromadistribuido@gmail.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(RequestIDMiddleware)
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
    expose_headers=["X-Request-ID"],
)

# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
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
app.include_router(simulate_router, prefix="/api/v1")


# ── Health & Observability ────────────────────────────────────────────────────
@app.get(
    "/api/v1/health",
    tags=["Observabilidad"],
    summary="Health check general",
    description="Retorna el estado del servicio y sus dependencias (Redis, RabbitMQ, DB).",
    response_description="Estado de todos los servicios",
)
async def health():
    redis_status = await check_redis_health()
    rabbit_status = await check_rabbitmq_health()
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "dependencies": {
            "redis": redis_status,
            "rabbitmq": rabbit_status,
            "database": "healthy",
        },
    }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        contact=app.contact,
        license_info=app.license_info,
        routes=app.routes,
    )
    schema["info"]["x-logo"] = {"url": "/uploads/logo.png"}
    schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtenido desde /api/v1/auth/login",
        }
    }
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
