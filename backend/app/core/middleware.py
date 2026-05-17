import logging
import time

from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.metrics import track_request_duration

logger = logging.getLogger(__name__)


SLI_EXCLUDE_PATHS = {"/metrics", "/health"}


class SLIMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in SLI_EXCLUDE_PATHS:
            return await call_next(request)

        start = time.monotonic()

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed = time.monotonic() - start
            track_request_duration(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=elapsed,
            )
            raise

        elapsed = time.monotonic() - start
        track_request_duration(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=elapsed,
        )

        if settings.SLI_DEBUG_LOGGING:
            logger.debug(
                "SLI: method=%s path=%s status=%d duration_ms=%.2f",
                request.method,
                request.url.path,
                response.status_code,
                elapsed * 1000,
            )

        return response
