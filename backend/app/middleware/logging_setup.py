import logging
import sys
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class AromaJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = settings.SERVICE_NAME
        log_record["environment"] = settings.ENVIRONMENT
        if "request_id" not in log_record:
            log_record["request_id"] = "-"
        if "event" not in log_record:
            log_record["event"] = record.getMessage()
        log_record["level"] = record.levelname
        log_record.setdefault("endpoint", "-")
        log_record.setdefault("status", "-")


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        AromaJsonFormatter(
            fmt="%(asctime)s %(request_id)s %(service)s %(event)s %(endpoint)s %(status)s %(levelname)s %(message)s"
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)

    # Silence noisy libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
