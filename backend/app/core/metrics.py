import time
from collections.abc import Callable
from functools import wraps

from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.core.config import settings

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests by method, path, and status group",
    labelnames=["method", "path", "status_group"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds by method and endpoint group",
    labelnames=["method", "endpoint_group"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

checkout_total = Counter(
    "checkout_total",
    "Checkout requests by status",
    labelnames=["status"],
)

checkout_duration_seconds = Histogram(
    "checkout_duration_seconds",
    "Checkout processing time in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

order_persistence_validations_total = Counter(
    "order_persistence_validations_total",
    "Order read-after-write validations by status",
    labelnames=["status"],
)

cart_consistency_validations_total = Counter(
    "cart_consistency_validations_total",
    "Cart consistency validations by status",
    labelnames=["status"],
)

db_available = Gauge("db_available", "PostgreSQL reachable (1 = up, 0 = down)")

db_connections_active = Gauge(
    "db_connections_active",
    "Active PostgreSQL connections",
)


def get_endpoint_group(path: str, method: str) -> str:
    if path.startswith("/auth"):
        return "auth"
    if path.startswith("/cart"):
        return "cart"
    if path.startswith("/checkout") or path.startswith("/orders"):
        return "checkout"
    if path == "/health":
        return "health"
    return "other"


def get_status_group(status_code: int) -> str:
    if status_code < 100:
        return "unknown"
    if status_code < 200:
        return "1xx"
    if status_code < 300:
        return "2xx"
    if status_code < 400:
        return "3xx"
    if status_code < 500:
        return "4xx"
    return "5xx"


def track_request_duration(method: str, path: str, status_code: int, duration: float):
    if not settings.SLI_ENABLED:
        return
    endpoint_group = get_endpoint_group(path, method)
    status_group = get_status_group(status_code)
    http_requests_total.labels(method=method, path=endpoint_group, status_group=status_group).inc()
    http_request_duration_seconds.labels(method=method, endpoint_group=endpoint_group).observe(duration)


async def metrics_endpoint() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


def track_checkout(status: str):
    if not settings.SLI_ENABLED:
        return
    checkout_total.labels(status=status).inc()


def track_checkout_duration(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.monotonic() - start
            if settings.SLI_ENABLED:
                checkout_duration_seconds.observe(elapsed)
            return result
        except Exception:
            elapsed = time.monotonic() - start
            if settings.SLI_ENABLED:
                checkout_duration_seconds.observe(elapsed)
            raise
    return wrapper
