from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/aroma_db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASSWORD: str = ""
    EMAILS_FROM: str = "noreply@aroma-distribuido.com"
    EMAILS_FROM_NAME: str = "Aroma-Distribuido"

    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    FRONTEND_URL: str = "http://localhost:5173"
    GOOGLE_CLIENT_ID: str = ""
    APPLE_CLIENT_ID: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_PRODUCTS: int = 300        # 5 minutes
    CACHE_TTL_CATEGORIES: int = 600      # 10 minutes
    CACHE_TTL_FEATURED: int = 120        # 2 minutes
    CACHE_TTL_SEARCH: int = 180          # 3 minutes

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://aroma_user:aroma_secret@localhost:5672/"
    RABBITMQ_EXCHANGE: str = "aroma_events"

    # Service metadata
    SERVICE_NAME: str = "aroma-backend"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
