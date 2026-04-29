"""
Redis client - VERSIÓN SIMPLIFICADA Y FUNCIONAL
Archivo: perfumeria_api/redis_client.py
Cambio: Simplificado para evitar errores de serialización
"""
import json
import redis
from typing import Any
from decimal import Decimal
from datetime import datetime, date

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

_redis_client = None

def _get_client():
    """Obtiene o crea cliente Redis."""
    global _redis_client
    if _redis_client:
        return _redis_client
    try:
        _redis_client = redis.StrictRedis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=REDIS_DB, 
            decode_responses=True,
            socket_connect_timeout=2
        )
        _redis_client.ping()
        print(f"✓ [REDIS] Conectado a {REDIS_HOST}:{REDIS_PORT}")
        return _redis_client
    except Exception as e:
        print(f"✗ [REDIS] Error de conexión: {e}")
        return None

def _serialize_value(obj):
    """Convierte objetos especiales a tipos serializables."""
    if isinstance(obj, (list, tuple)):
        return [_serialize_value(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _serialize_value(val) for key, val in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

def get_cache(key: str) -> Any:
    """Obtiene valor del cache."""
    client = _get_client()
    if not client:
        return None
    try:
        val = client.get(key)
        if val is None:
            print(f"✗ [REDIS] CACHE MISS: {key}")
            return None
        data = json.loads(val)
        print(f"✓ [REDIS] CACHE HIT: {key}")
        return data
    except Exception as e:
        print(f"✗ [REDIS] Error GET: {e}")
        return None

def set_cache(key: str, value: Any, ttl: int = 60) -> bool:
    """Guarda valor en cache."""
    client = _get_client()
    if not client:
        print(f"✗ [REDIS] No hay conexión para SET {key}")
        return False
    try:
        # Serializar y limpiar los datos
        cleaned_value = _serialize_value(value)
        json_str = json.dumps(cleaned_value)
        
        # Guardar en Redis
        result = client.set(key, json_str, ex=ttl)
        
        if result:
            print(f"✓ [REDIS] GUARDADO: {key} ({len(json_str)} bytes, TTL={ttl}s)")
            return True
        else:
            print(f"✗ [REDIS] Falló al guardar {key}")
            return False
    except Exception as e:
        print(f"✗ [REDIS] Error SET: {e}")
        return False

def delete_cache(*keys: str) -> bool:
    """Elimina claves del cache."""
    client = _get_client()
    if not client:
        return False
    try:
        if keys:
            deleted = client.delete(*keys)
            print(f"✓ [REDIS] ELIMINADO: {deleted} claves")
            return True
        return False
    except Exception as e:
        print(f"✗ [REDIS] Error DELETE: {e}")
        return False
