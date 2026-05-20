import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import track_request


EXCLUDE_PATHS = {"/metrics", "/health"}


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in EXCLUDE_PATHS:
            return await call_next(request)

        start = time.monotonic()

        try:
            response = await call_next(request)
        except Exception:
            elapsed = time.monotonic() - start
            route = request.scope.get("route")
            path = route.path if route else request.url.path
            track_request(
                method=request.method,
                path=path,
                status_code=500,
                duration=elapsed,
            )
            raise

        elapsed = time.monotonic() - start
        route = request.scope.get("route")
        path = route.path if route else request.url.path
        track_request(
            method=request.method,
            path=path,
            status_code=response.status_code,
            duration=elapsed,
        )

        return response
