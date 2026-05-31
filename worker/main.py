"""
Aroma-Distribuido Worker Service
=================================
Servicio independiente que consume mensajes de RabbitMQ y procesa:
  - Confirmaciones de pedidos (correo)
  - Actualizaciones de inventario
  - Notificaciones de usuario registrado
  - Eventos futuros (extensible)

Se conecta automáticamente y reconecta si RabbitMQ cae.
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

import aio_pika
from aio_pika import ExchangeType
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
class WorkerJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = "aroma-worker"
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record.setdefault("event", record.getMessage())
        log_record.setdefault("request_id", "-")

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(WorkerJsonFormatter())
logging.getLogger().handlers = [handler]
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("aroma-worker")

# ── Config ─────────────────────────────────────────────────────────────────────
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://aroma_user:aroma_secret@rabbitmq:5672/")
EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE", "aroma_events")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SERVICE_NAME = "aroma-worker"

QUEUES = [
    ("aroma.orders", "order.*"),
    ("aroma.users", "user.*"),
    ("aroma.inventory", "inventory.*"),
    ("aroma.notifications", "#"),
]

RECONNECT_DELAY = 5  # seconds


# ── Handlers ───────────────────────────────────────────────────────────────────

async def handle_order_created(payload: dict) -> None:
    order_id = payload.get("order_id")
    order_number = payload.get("order_number")
    email = payload.get("email")
    total = payload.get("total")

    logger.info(
        "Processing order confirmation",
        extra={
            "event": "worker_order_created",
            "order_id": order_id,
            "order_number": order_number,
            "email": email,
        },
    )
    # In production: send confirmation email via SMTP here
    await asyncio.sleep(0.1)  # Simulate async email send
    logger.info(
        "Order confirmation email sent",
        extra={
            "event": "worker_email_sent",
            "order_id": order_id,
            "email": email,
            "status": "success",
        },
    )


async def handle_order_confirmed(payload: dict) -> None:
    order_id = payload.get("order_id")
    new_status = payload.get("new_status")
    email = payload.get("email")

    logger.info(
        "Processing order status notification",
        extra={
            "event": "worker_order_confirmed",
            "order_id": order_id,
            "new_status": new_status,
        },
    )
    await asyncio.sleep(0.05)
    logger.info(
        "Order status notification sent",
        extra={
            "event": "worker_notification_sent",
            "order_id": order_id,
            "status": "success",
        },
    )


async def handle_order_shipped(payload: dict) -> None:
    order_id = payload.get("order_id")
    tracking_number = payload.get("tracking_number")

    logger.info(
        "Processing shipping notification",
        extra={
            "event": "worker_order_shipped",
            "order_id": order_id,
            "tracking_number": tracking_number,
        },
    )
    await asyncio.sleep(0.05)


async def handle_user_registered(payload: dict) -> None:
    user_id = payload.get("user_id")
    email = payload.get("email")

    logger.info(
        "Processing welcome email",
        extra={
            "event": "worker_user_registered",
            "user_id": user_id,
            "email": email,
        },
    )
    await asyncio.sleep(0.1)
    logger.info(
        "Welcome email queued",
        extra={
            "event": "worker_welcome_email_sent",
            "user_id": user_id,
            "status": "success",
        },
    )


async def handle_inventory_updated(payload: dict) -> None:
    product_id = payload.get("product_id")
    variant_id = payload.get("variant_id")
    new_stock = payload.get("new_stock")

    logger.info(
        "Processing inventory update",
        extra={
            "event": "worker_inventory_updated",
            "product_id": product_id,
            "variant_id": variant_id,
            "new_stock": new_stock,
        },
    )
    # In production: invalidate Redis cache, trigger low-stock alerts, etc.
    await asyncio.sleep(0.02)


async def handle_unknown(event_type: str, payload: dict) -> None:
    logger.warning(
        "Unknown event type received",
        extra={
            "event": "worker_unknown_event",
            "event_type": event_type,
            "payload_keys": list(payload.keys()),
        },
    )


EVENT_HANDLERS = {
    "order.created": handle_order_created,
    "order.confirmed": handle_order_confirmed,
    "order.shipped": handle_order_shipped,
    "user.registered": handle_user_registered,
    "inventory.updated": handle_inventory_updated,
}


async def process_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process(requeue=True):
        try:
            body = json.loads(message.body.decode())
            event_type = body.get("event", "unknown")
            payload = body.get("payload", {})
            timestamp = body.get("timestamp", "-")

            logger.info(
                "Message received",
                extra={
                    "event": "worker_message_received",
                    "event_type": event_type,
                    "timestamp": timestamp,
                    "queue": message.routing_key,
                },
            )

            handler_fn = EVENT_HANDLERS.get(event_type)
            if handler_fn:
                await handler_fn(payload)
            else:
                await handle_unknown(event_type, payload)

        except json.JSONDecodeError as exc:
            logger.error(
                "Invalid JSON message",
                extra={"event": "worker_json_error", "error": str(exc)},
            )
        except Exception as exc:
            logger.error(
                "Error processing message",
                extra={"event": "worker_processing_error", "error": str(exc)},
            )
            raise  # triggers requeue=True


async def start_consuming(connection: aio_pika.Connection) -> None:
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=5)

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.TOPIC,
        durable=True,
    )

    for queue_name, routing_key in QUEUES:
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, routing_key=routing_key)
        await queue.consume(process_message)
        logger.info(
            "Queue bound and consuming",
            extra={"event": "worker_queue_bound", "queue": queue_name, "routing_key": routing_key},
        )

    logger.info(
        "Worker ready — waiting for messages",
        extra={"event": "worker_ready", "queues": [q[0] for q in QUEUES]},
    )
    await asyncio.Future()  # Run forever


async def main() -> None:
    logger.info(
        "Aroma Worker starting",
        extra={"event": "worker_starting", "rabbitmq_url": RABBITMQ_URL.split("@")[-1]},
    )

    while True:
        try:
            connection = await aio_pika.connect_robust(
                RABBITMQ_URL,
                timeout=10,
                reconnect_interval=RECONNECT_DELAY,
            )
            logger.info(
                "Connected to RabbitMQ",
                extra={"event": "worker_connected"},
            )
            await start_consuming(connection)
        except aio_pika.exceptions.AMQPConnectionError as exc:
            logger.error(
                "RabbitMQ connection error — retrying",
                extra={
                    "event": "worker_connection_error",
                    "error": str(exc),
                    "retry_in": RECONNECT_DELAY,
                },
            )
            await asyncio.sleep(RECONNECT_DELAY)
        except KeyboardInterrupt:
            logger.info("Worker stopped by user", extra={"event": "worker_stopped"})
            break
        except Exception as exc:
            logger.error(
                "Unexpected error — retrying",
                extra={"event": "worker_unexpected_error", "error": str(exc)},
            )
            await asyncio.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    asyncio.run(main())
