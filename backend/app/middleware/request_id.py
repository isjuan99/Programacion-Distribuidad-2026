import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        start_time = time.time()

        request.state.request_id = request_id
        request.state.start_time = start_time

        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "event": "request_started",
                "method": request.method,
                "endpoint": str(request.url.path),
                "client": request.client.host if request.client else "unknown",
            },
        )

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id

        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "event": "request_completed",
                "method": request.method,
                "endpoint": str(request.url.path),
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
