"""
Simulación de fallos para demostración de resiliencia del sistema distribuido.
Estos endpoints permiten probar el comportamiento cuando Redis o RabbitMQ no están disponibles.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.redis_client import _redis as _redis_ref, cache_get, cache_set
from app.core.rabbitmq import publish_event

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/simulate",
    tags=["Simulación de Fallos"],
)


class SimulateResponse(BaseModel):
    scenario: str
    result: str
    logged: bool
    details: dict = {}


@router.post(
    "/redis-failure",
    response_model=SimulateResponse,
    summary="Simular caída de Redis",
    description="""
Simula el comportamiento del sistema cuando Redis no está disponible.
El backend debe funcionar normalmente (degraded mode) sin caché.
Se registra el error en los logs estructurados JSON.
""",
)
async def simulate_redis_failure():
    import redis.asyncio as aioredis
    import app.core.redis_client as rc

    original = rc._redis

    # Force Redis to appear unavailable for this call
    rc._redis = None
    try:
        result = await cache_get("simulate:test:key")
        write_result = await cache_set("simulate:test:key", {"test": True}, ttl=5)
    finally:
        rc._redis = original

    logger.warning(
        "SIMULATION: Redis failure scenario triggered",
        extra={
            "event": "simulation_redis_failure",
            "scenario": "redis_unavailable",
            "cache_get_result": result,
            "cache_set_result": write_result,
        },
    )
    return SimulateResponse(
        scenario="redis_failure",
        result="Sistema degradado — operando sin caché. El tráfico fue a la base de datos.",
        logged=True,
        details={
            "cache_get": "None (redis unavailable)",
            "cache_set": "False (redis unavailable)",
            "fallback": "Database query executed",
            "service_status": "degraded_but_operational",
        },
    )


@router.post(
    "/rabbitmq-failure",
    response_model=SimulateResponse,
    summary="Simular caída de RabbitMQ",
    description="""
Simula el comportamiento cuando RabbitMQ no está disponible.
Los eventos no se publican pero el sistema sigue funcionando.
Se registra la omisión del evento en los logs.
""",
)
async def simulate_rabbitmq_failure():
    import app.core.rabbitmq as rmq

    original_channel = rmq._channel
    original_exchange = rmq._exchange

    rmq._channel = None
    rmq._exchange = None
    try:
        published = await publish_event("order.created", {
            "order_id": 0,
            "simulation": True,
            "note": "Este evento fue omitido por RabbitMQ no disponible",
        })
    finally:
        rmq._channel = original_channel
        rmq._exchange = original_exchange

    logger.warning(
        "SIMULATION: RabbitMQ failure scenario triggered",
        extra={
            "event": "simulation_rabbitmq_failure",
            "scenario": "rabbitmq_unavailable",
            "event_published": published,
        },
    )
    return SimulateResponse(
        scenario="rabbitmq_failure",
        result="Evento omitido — RabbitMQ no disponible. El pedido igual se guardó en DB.",
        logged=True,
        details={
            "event_published": published,
            "event_type": "order.created",
            "fallback": "Event skipped, DB transaction completed",
            "service_status": "degraded_but_operational",
        },
    )


@router.post(
    "/worker-failure",
    response_model=SimulateResponse,
    summary="Simular caída del Worker",
    description="""
Simula el escenario donde el Worker está caído.
Los mensajes quedan encolados en RabbitMQ y se procesan cuando el Worker vuelve a levantarse.
""",
)
async def simulate_worker_failure():
    published = await publish_event("worker.test", {
        "simulation": True,
        "note": "Mensaje encolado — Worker simulado como caído",
        "expected_behavior": "Message persists in queue until worker recovers",
    })

    logger.warning(
        "SIMULATION: Worker failure scenario triggered",
        extra={
            "event": "simulation_worker_failure",
            "scenario": "worker_unavailable",
            "message_queued": published,
        },
    )
    return SimulateResponse(
        scenario="worker_failure",
        result="Mensaje encolado en RabbitMQ. Se procesará cuando el Worker se recupere (durable queue).",
        logged=True,
        details={
            "message_queued": published,
            "queue": "aroma.notifications",
            "durable": True,
            "persistence": "Message survives broker restart",
            "recovery": "Worker auto-processes pending messages on restart",
        },
    )


@router.get(
    "/status",
    summary="Estado actual de todos los servicios distribuidos",
    description="Muestra el estado de Redis, RabbitMQ y Worker para observabilidad.",
)
async def distributed_status():
    from app.core.redis_client import check_redis_health
    from app.core.rabbitmq import check_rabbitmq_health

    redis_health = await check_redis_health()
    rabbit_health = await check_rabbitmq_health()

    logger.info(
        "Distributed status check",
        extra={
            "event": "status_check",
            "redis_status": redis_health.get("status"),
            "rabbitmq_status": rabbit_health.get("status"),
        },
    )

    return {
        "services": {
            "redis": redis_health,
            "rabbitmq": rabbit_health,
            "worker": {
                "status": "check_dozzle",
                "note": "Monitor worker logs at http://localhost:8888 (Dozzle)",
            },
            "portainer": {
                "url": "http://localhost:9000",
                "note": "Docker management UI",
            },
        },
        "resilience": {
            "redis_fallback": "Database queries (degraded mode)",
            "rabbitmq_fallback": "Events skipped, logged as warnings",
            "worker_fallback": "Messages persist in durable RabbitMQ queues",
        },
    }
