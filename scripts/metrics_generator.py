"""Standalone Prometheus metrics generator for local Grafana development.

Generates synthetic e-commerce metrics matching the backend's metric names.
Run without Docker/PostgreSQL — works directly on Windows 11.

Usage:
    uv run python scripts/metrics_generator.py --port 8001
"""
import argparse
import os
import random
import signal
import socketserver
import sys
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler

from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

REQUESTS_PER_SECOND = 8
GENERATOR_INTERVAL = 3

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

process_cpu_seconds_total = Gauge(
    "app_process_cpu_seconds_total",
    "Total user and system CPU time spent in seconds",
)

process_resident_memory_bytes = Gauge(
    "app_process_resident_memory_bytes",
    "Resident memory size in bytes",
)

psutil = None
try:
    import psutil as _psutil
    psutil = _psutil
except ImportError:
    pass

ENDPOINT_GROUPS = ["auth", "cart", "checkout", "health", "other"]
METHODS = ["GET", "POST", "PUT", "DELETE"]
PATH_BY_GROUP = {
    "auth": ["/auth/login", "/auth/register", "/auth/me"],
    "cart": ["/cart", "/cart/items", "/cart/items/1"],
    "checkout": ["/checkout", "/orders", "/orders/1"],
    "health": ["/health"],
    "other": ["/products", "/products/1", "/categories"],
}


def _random_status():
    r = random.random()
    if r < 0.95:
        code = random.choice([200, 201, 204])
        return "2xx", code
    if r < 0.98:
        code = random.choice([400, 401, 403, 404, 422])
        return "4xx", code
    code = random.choice([500, 502, 503])
    return "5xx", code


def _generate_batch():
    n = random.randint(
        max(1, REQUESTS_PER_SECOND * GENERATOR_INTERVAL - 5),
        REQUESTS_PER_SECOND * GENERATOR_INTERVAL + 5,
    )
    for _ in range(n):
        group = random.choices(ENDPOINT_GROUPS, weights=[0.15, 0.20, 0.10, 0.05, 0.50], k=1)[0]
        method = random.choice(METHODS)
        path = random.choice(PATH_BY_GROUP[group])
        status_group, _ = _random_status()

        http_requests_total.labels(method=method, path=group, status_group=status_group).inc()

        if group == "auth":
            d = abs(random.gauss(0.10, 0.05))
        elif group in ("checkout", "orders"):
            d = abs(random.gauss(0.80, 0.30))
        elif group == "cart":
            d = abs(random.gauss(0.05, 0.02))
        elif group == "health":
            d = abs(random.gauss(0.01, 0.005))
        else:
            d = abs(random.gauss(0.05, 0.03))
        http_request_duration_seconds.labels(method=method, endpoint_group=group).observe(d)

    if random.random() < 0.90:
        checkout_total.labels(status="success").inc()
    else:
        checkout_total.labels(status="failure").inc()
    checkout_duration_seconds.observe(abs(random.gauss(0.80, 0.30)))

    order_ok = random.random() < 0.99
    order_persistence_validations_total.labels(status="success" if order_ok else "failure").inc()

    cart_ok = random.random() < 0.98
    cart_consistency_validations_total.labels(status="success" if cart_ok else "failure").inc()

    db_available.set(1 if random.random() > 0.001 else 0)
    db_connections_active.set(random.randint(5, 60))

    if psutil:
        try:
            proc = psutil.Process()
            cpu = proc.cpu_times()
            process_cpu_seconds_total.set(cpu.user + cpu.system)
            process_resident_memory_bytes.set(proc.memory_info().rss)
            return
        except Exception:
            pass
    process_cpu_seconds_total.set(random.uniform(100, 500))
    process_resident_memory_bytes.set(random.randint(80_000_000, 200_000_000))


def _seed_initial_metrics():
    for _ in range(200):
        _generate_batch()


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            payload = generate_latest()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
            self.wfile.flush()
        elif self.path == "/health":
            body = b'{"status":"ok","generator":"metrics_generator"}'
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
        else:
            body = b'{"detail":"Not Found"}'
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()

    def log_message(self, format, *args):
        pass


def background_loop(stop_event):
    _seed_initial_metrics()
    while not stop_event.is_set():
        _generate_batch()
        stop_event.wait(GENERATOR_INTERVAL)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description="Synthetic Prometheus metrics generator")
    parser.add_argument("--port", type=int, default=8001, help="HTTP server port (default: 8001)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    args = parser.parse_args()

    stop_event = threading.Event()

    def shutdown_handler(signum, frame):
        print(f"\n[metrics-generator] Signal received, shutting down...")
        stop_event.set()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    t = threading.Thread(target=background_loop, args=(stop_event,), daemon=True)
    t.start()

    server = ThreadedHTTPServer((args.host, args.port), MetricsHandler)

    print(f"[metrics-generator] Starting on http://{args.host}:{args.port}/metrics")
    print(f"[metrics-generator] Health check: http://{args.host}:{args.port}/health")
    print(f"[metrics-generator] Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[metrics-generator] Shutting down...")
    finally:
        stop_event.set()
        server.shutdown()


if __name__ == "__main__":
    main()
