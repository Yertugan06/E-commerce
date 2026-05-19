"""Synthetic Prometheus metrics generator matching the refined SLI Matrix.

Maps to: FastAPI middleware, ASGI logs, structured application logs, Application Validation, and DB ops.
SLIs: API Availability, Checkout Success Rate, Cart/Order Read Latency, Cart Update/Checkout/Auth Latency, Cart Consistency Rate.
"""
import argparse
import random
import signal
import socketserver
import sys
import threading
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Operational Knobs
REQUESTS_PER_SECOND = 12
GENERATOR_INTERVAL = 2

# --- METRIC DEFINITIONS (Directly Mapping to SLI Matrix) ---

# SLI 1: API Availability (FastAPI Middleware — responses < 500 / total)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests by method, path, and status group (Middleware counters)",
    labelnames=["method", "path", "status_group"],
)

# SLIs 3-6, 8: Per-Endpoint Latencies (ASGI Logs — path granularity)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds (ASGI logs)",
    labelnames=["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# SLI 2: Checkout Success Rate (Structured Application Logs — 200/201 for POST /checkout)
checkout_total = Counter(
    "checkout_total",
    "Checkout transaction counts tracking structured log output",
    labelnames=["status"],
)

checkout_duration_seconds = Histogram(
    "checkout_duration_seconds",
    "Processing time specifically for the checkout pipeline",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)

# SLI 8: Cart Consistency Rate (Application Validation — success rate)
cart_consistency_validations_total = Counter(
    "cart_consistency_validations_total",
    "Validations verifying carts reflect latest updates within 1s",
    labelnames=["status"],
)

# SLI 2: Database Availability (pg_isready health check simulation — kept for ops)
db_available = Gauge(
    "db_available", 
    "PostgreSQL reachability status based on pg_isready (1 = Up, 0 = Down)"
)

# Ops: DB Connection Usage (pg_stat_activity tracking)
db_connections_active = Gauge(
    "db_connections_active",
    "Active PostgreSQL connections sourced from pg_stat_activity",
)

# Ops: Container CPU / Memory Usage (docker stats tracking)
app_process_cpu_seconds_total = Counter(
    "app_process_cpu_seconds_total",
    "Container resource utilization: CPU seconds used",
)

app_process_resident_memory_bytes = Gauge(
    "app_process_resident_memory_bytes",
    "Container resource utilization: Memory RSS usage in bytes",
)


def _simulate_network_transaction():
    """Generates a batch of traffic matching the requested SLI paths."""
    
    # 1. Determine HTTP Response code following SLI targets (>99.5% success target)
    rand_status = random.random()
    if rand_status < 0.996:
        status_group = "2xx"
    elif rand_status < 0.999:
        status_group = "4xx"
    else:
        status_group = "5xx"

    # 2. Pick a specific endpoint matching the refined SLI set
    # API Availability: tracks all status groups
    # Cart Read Latency: GET /cart
    # Order Read Latency: GET /orders
    # Cart Update Latency: POST /cart/items
    # Checkout Latency / Success Rate: POST /checkout
    # Auth Latency: POST /auth/login
    sli_flow = random.choices(
        ["read_cart", "read_orders", "write_cart", "checkout", "auth", "other"],
        weights=[0.20, 0.20, 0.25, 0.15, 0.10, 0.10],
        k=1
    )[0]

    method = "GET"
    path = "/other"
    latency = abs(random.gauss(0.04, 0.01))

    if sli_flow == "read_cart":
        method, path = "GET", "/cart"
        latency = abs(random.gauss(0.06, 0.015))
    elif sli_flow == "read_orders":
        method, path = "GET", "/orders"
        latency = abs(random.gauss(0.09, 0.02))
    elif sli_flow == "write_cart":
        method, path = "POST", "/cart/items"
        latency = abs(random.gauss(0.12, 0.03))
    elif sli_flow == "checkout":
        method, path = "POST", "/checkout"
        latency = abs(random.gauss(0.38, 0.08))
        
        # Track structured log output for Checkout Success Rate
        if status_group != "5xx" and random.random() > 0.01:
            checkout_total.labels(status="success").inc()
        else:
            checkout_total.labels(status="failure").inc()
        checkout_duration_seconds.observe(latency)
        
    elif sli_flow == "auth":
        method, path = "POST", "/auth/login"
        latency = abs(random.gauss(0.18, 0.04))

    # Increment core metrics
    http_requests_total.labels(method=method, path=path, status_group=status_group).inc()
    http_request_duration_seconds.labels(method=method, path=path).observe(latency)


def _generate_metrics_batch():
    """Fires a collection of transactions across an interval window."""
    iterations = random.randint(REQUESTS_PER_SECOND * 1, REQUESTS_PER_SECOND * 2)
    for _ in range(iterations):
        _simulate_network_transaction()

    # SLI 8: Cart Consistency Validations (Propagation lag checks)
    if random.random() < 0.9992:
        cart_consistency_validations_total.labels(status="success").inc()
    else:
        cart_consistency_validations_total.labels(status="failure").inc()

    # Ops: Database Availability (pg_isready check)
    db_available.set(1 if random.random() > 0.0001 else 0)

    # Ops: DB Connection Usage (pg_stat_activity)
    db_connections_active.set(random.randint(18, 29))

    # Ops: CPU & Memory Consumption
    app_process_cpu_seconds_total.inc(random.uniform(0.03, 0.05) * GENERATOR_INTERVAL)
    app_process_resident_memory_bytes.set(random.randint(135_000_000, 150_000_000))


def background_loop(stop_event):
    # Seed dynamic data patterns instantly on launch
    for _ in range(100):
        _generate_metrics_batch()
    while not stop_event.is_set():
        _generate_metrics_batch()
        stop_event.wait(GENERATOR_INTERVAL)


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
        elif self.path == "/health":
            body = b'{"status":"ok"}'
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

    def log_message(self, format, *args):
        pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    stop_event = threading.Event()

    def shutdown_handler(signum, frame):
        stop_event.set()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    t = threading.Thread(target=background_loop, args=(stop_event,), daemon=True)
    t.start()

    print(f"[SLI Core Engine] Hosting exporter path at http://{args.host}:{args.port}/metrics")
    server = ThreadedHTTPServer((args.host, args.port), MetricsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        server.shutdown()


if __name__ == "__main__":
    main()