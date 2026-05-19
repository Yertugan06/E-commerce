import time
from collections.abc import Callable
from functools import wraps

from prometheus_client import Counter, Gauge, Histogram, REGISTRY
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests by method, path, and status group",
    labelnames=["method", "path", "status_group"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds by method and path",
    labelnames=["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
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

app_process_cpu_seconds_total = Gauge(
    "app_process_cpu_seconds_total",
    "Total user and system CPU time spent in seconds",
)

app_process_resident_memory_bytes = Gauge(
    "app_process_resident_memory_bytes",
    "Resident memory size in bytes",
)


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


def track_request(method: str, path: str, status_code: int, duration: float):
    status_group = get_status_group(status_code)
    http_requests_total.labels(method=method, path=path, status_group=status_group).inc()
    http_request_duration_seconds.labels(method=method, path=path).observe(duration)


async def metrics_endpoint() -> Response:
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )


def track_checkout(status: str):
    checkout_total.labels(status=status).inc()


def track_checkout_duration(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            result = await func(*args, **kwargs)
            checkout_duration_seconds.observe(time.monotonic() - start)
            return result
        except Exception:
            checkout_duration_seconds.observe(time.monotonic() - start)
            raise
    return wrapper


def collect_process_metrics():
    try:
        import psutil
        process = psutil.Process()
        cpu_time = process.cpu_times()
        app_process_cpu_seconds_total.set(cpu_time.user + cpu_time.system)
        app_process_resident_memory_bytes.set(process.memory_info().rss)
    except ImportError:
        pass
    except Exception:
        pass
