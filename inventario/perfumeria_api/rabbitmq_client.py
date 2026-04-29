"""
RabbitMQ client helpers.
Creado: funciones publish/consume con degradación a procesamiento síncrono si RabbitMQ no disponible.
Archivo: perfumeria_api/rabbitmq_client.py
"""
import json
import pika
from typing import Callable

RABBIT_HOST = "localhost"
RABBIT_PORT = 5672
RABBIT_USER = "guest"
RABBIT_PASS = "guest"

def _get_connection():
    try:
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
        params = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT, credentials=credentials)
        return pika.BlockingConnection(params)
    except Exception:
        return None

def publish_message(queue: str, message: dict) -> bool:
    """Publica un mensaje JSON en la cola. Retorna True si se publicó, False si RabbitMQ no disponible."""
    conn = _get_connection()
    if not conn:
        return False
    try:
        channel = conn.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
        conn.close()
        return True
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        return False

def consume_messages(queue: str, callback: Callable[[dict], None]):
    """Consume mensajes de la cola y ejecuta callback por cada mensaje (bloqueante)."""
    conn = _get_connection()
    if not conn:
        raise RuntimeError("RabbitMQ no disponible")
    channel = conn.channel()
    channel.queue_declare(queue=queue, durable=True)

    def _on_message(ch, method, properties, body):
        try:
            payload = json.loads(body)
            callback(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=_on_message)
    try:
        channel.start_consuming()
    finally:
        try:
            conn.close()
        except Exception:
            pass
