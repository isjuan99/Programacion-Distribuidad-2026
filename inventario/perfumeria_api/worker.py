"""
Worker para procesar ordenes desde RabbitMQ.
Archivo: perfumeria_api/worker.py
Ejecutar: python perfumeria_api/worker.py
"""
import sys
import traceback
from perfumeria_api.rabbitmq_client import consume_messages
from database import obtener_conexion

QUEUE_NAME = "ordenes_queue"

def process_order(message: dict):
    """Callback que recibe órdenes en cola sin modificar su estado automáticamente."""
    try:
        orden_id = message.get("orden_id")
        if not orden_id:
            return
        print(f"Worker: orden recibida en cola y marcada para revisión manual: {orden_id}")
    except Exception:
        traceback.print_exc()

def main():
    try:
        consume_messages(QUEUE_NAME, process_order)
    except Exception as e:
        print("Worker: no se puede conectar a RabbitMQ:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
