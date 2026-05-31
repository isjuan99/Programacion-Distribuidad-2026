import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    global _redis
    if _redis is None:
        try:
            _redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            await _redis.ping()
            logger.info("Redis connected", extra={"event": "redis_connected"})
        except Exception as exc:
            logger.warning(
                "Redis unavailable — running without cache",
                extra={"event": "redis_unavailable", "error": str(exc)},
            )
            _redis = None
    return _redis


async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    if r is None:
        return None
    try:
        raw = await r.get(key)
        return json.loads(raw) if raw else None
    except Exception as exc:
        logger.warning(
            "Redis get failed",
            extra={"event": "redis_get_error", "key": key, "error": str(exc)},
        )
        return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    r = await get_redis()
    if r is None:
        return False
    try:
        await r.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as exc:
        logger.warning(
            "Redis set failed",
            extra={"event": "redis_set_error", "key": key, "error": str(exc)},
        )
        return False


async def cache_delete(key: str) -> bool:
    r = await get_redis()
    if r is None:
        return False
    try:
        await r.delete(key)
        return True
    except Exception as exc:
        logger.warning(
            "Redis delete failed",
            extra={"event": "redis_delete_error", "key": key, "error": str(exc)},
        )
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a glob pattern. Returns count deleted."""
    r = await get_redis()
    if r is None:
        return 0
    try:
        keys = await r.keys(pattern)
        if keys:
            return await r.delete(*keys)
        return 0
    except Exception as exc:
        logger.warning(
            "Redis pattern delete failed",
            extra={"event": "redis_pattern_delete_error", "pattern": pattern, "error": str(exc)},
        )
        return 0


async def invalidate_product_caches(product_id: Optional[int] = None) -> None:
    """Invalidate all product-related cache entries."""
    patterns = [
        "products:list:*",
        "products:featured:*",
        "categories:*",
        "search:*",
    ]
    if product_id:
        patterns.append(f"products:detail:{product_id}")

    for p in patterns:
        deleted = await cache_delete_pattern(p)
        logger.info(
            "Cache invalidated",
            extra={"event": "cache_invalidated", "pattern": p, "deleted_keys": deleted},
        )


async def check_redis_health() -> dict:
    r = await get_redis()
    if r is None:
        return {"status": "unavailable", "error": "Connection failed"}
    try:
        await r.ping()
        info = await r.info("server")
        return {
            "status": "healthy",
            "version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
