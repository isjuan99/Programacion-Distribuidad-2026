import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aio_pika
from aio_pika import ExchangeType

from app.core.config import settings

logger = logging.getLogger(__name__)

_connection: Optional[aio_pika.Connection] = None
_channel: Optional[aio_pika.Channel] = None
_exchange: Optional[aio_pika.Exchange] = None


QUEUE_ORDERS = "aroma.orders"
QUEUE_USERS = "aroma.users"
QUEUE_INVENTORY = "aroma.inventory"
QUEUE_NOTIFICATIONS = "aroma.notifications"

EVENT_ORDER_CREATED = "order.created"
EVENT_ORDER_CONFIRMED = "order.confirmed"
EVENT_ORDER_SHIPPED = "order.shipped"
EVENT_USER_REGISTERED = "user.registered"
EVENT_INVENTORY_UPDATED = "inventory.updated"


async def get_rabbitmq_channel() -> Optional[aio_pika.Channel]:
    global _connection, _channel, _exchange
    if _channel is not None and not _channel.is_closed:
        return _channel
    try:
        _connection = await aio_pika.connect_robust(
            settings.RABBITMQ_URL,
            timeout=5,
        )
        _channel = await _connection.channel()
        await _channel.set_qos(prefetch_count=10)

        _exchange = await _channel.declare_exchange(
            settings.RABBITMQ_EXCHANGE,
            ExchangeType.TOPIC,
            durable=True,
        )

        for queue_name, routing_key in [
            (QUEUE_ORDERS, "order.*"),
            (QUEUE_USERS, "user.*"),
            (QUEUE_INVENTORY, "inventory.*"),
            (QUEUE_NOTIFICATIONS, "#"),
        ]:
            queue = await _channel.declare_queue(queue_name, durable=True)
            await queue.bind(_exchange, routing_key=routing_key)

        logger.info(
            "RabbitMQ connected",
            extra={"event": "rabbitmq_connected", "exchange": settings.RABBITMQ_EXCHANGE},
        )
        return _channel
    except Exception as exc:
        logger.warning(
            "RabbitMQ unavailable — events disabled",
            extra={"event": "rabbitmq_unavailable", "error": str(exc)},
        )
        _connection = None
        _channel = None
        _exchange = None
        return None


async def publish_event(event_type: str, payload: dict[str, Any]) -> bool:
    global _exchange
    channel = await get_rabbitmq_channel()
    if channel is None or _exchange is None:
        logger.warning(
            "Event not published — RabbitMQ unavailable",
            extra={"event": "event_skipped", "event_type": event_type},
        )
        return False
    try:
        message_body = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": settings.SERVICE_NAME,
            "payload": payload,
        }
        await _exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body, default=str).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=event_type,
        )
        logger.info(
            "Event published",
            extra={"event": "event_published", "event_type": event_type, "payload_keys": list(payload.keys())},
        )
        return True
    except Exception as exc:
        logger.error(
            "Failed to publish event",
            extra={"event": "event_publish_error", "event_type": event_type, "error": str(exc)},
        )
        return False


async def check_rabbitmq_health() -> dict:
    channel = await get_rabbitmq_channel()
    if channel is None:
        return {"status": "unavailable", "error": "Connection failed"}
    try:
        if _connection and not _connection.is_closed:
            return {
                "status": "healthy",
                "exchange": settings.RABBITMQ_EXCHANGE,
                "queues": [QUEUE_ORDERS, QUEUE_USERS, QUEUE_INVENTORY, QUEUE_NOTIFICATIONS],
            }
        return {"status": "error", "error": "Connection closed"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


async def close_rabbitmq() -> None:
    global _connection, _channel, _exchange
    if _channel and not _channel.is_closed:
        await _channel.close()
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None
    _channel = None
    _exchange = None
