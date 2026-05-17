import logging
import os
import subprocess
import time

import httpx
from prometheus_client import Counter, Gauge, start_http_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("autoscaler")

PROMETHEUS_URL = os.getenv("AUTOSCALER_PROMETHEUS_URL", "http://prometheus:9090")
COMPOSE_PROJECT = os.getenv("AUTOSCALER_COMPOSE_PROJECT", "ecommerce")
SERVICE_NAME = os.getenv("AUTOSCALER_SERVICE_NAME", "backend")

MIN_REPLICAS = int(os.getenv("AUTOSCALER_MIN_REPLICAS", "1"))
MAX_REPLICAS = int(os.getenv("AUTOSCALER_MAX_REPLICAS", "5"))
SCALE_UP_THRESHOLD = float(os.getenv("AUTOSCALER_SCALE_UP_THRESHOLD", "0.70"))
SCALE_DOWN_THRESHOLD = float(os.getenv("AUTOSCALER_SCALE_DOWN_THRESHOLD", "0.30"))
COOLDOWN_SECONDS = int(os.getenv("AUTOSCALER_COOLDOWN_SECONDS", "60"))
P95_LATENCY_THRESHOLD = float(os.getenv("AUTOSCALER_P95_LATENCY_THRESHOLD", "1.0"))
REQUEST_RATE_THRESHOLD = float(os.getenv("AUTOSCALER_REQUEST_RATE_THRESHOLD", "50"))
POLL_INTERVAL = int(os.getenv("AUTOSCALER_POLL_INTERVAL", "15"))
METRICS_PORT = int(os.getenv("AUTOSCALER_METRICS_PORT", "9100"))

replicas_current = Gauge("autoscaler_replicas_current", "Current number of backend replicas")
replicas_desired = Gauge("autoscaler_replicas_desired", "Desired number of backend replicas")
replicas_min = Gauge("autoscaler_replicas_min", "Minimum allowed replicas")
replicas_max = Gauge("autoscaler_replicas_max", "Maximum allowed replicas")
scale_up_events = Counter("autoscaler_scale_up_events_total", "Total scale-up events")
scale_down_events = Counter("autoscaler_scale_down_events_total", "Total scale-down events")
last_evaluation = Gauge("autoscaler_last_evaluation_seconds", "Timestamp of last evaluation")

replicas_min.set(MIN_REPLICAS)
replicas_max.set(MAX_REPLICAS)


def get_current_replicas() -> int:
    result = subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, "ps", "--format", "{{.Name}}"],
        capture_output=True, text=True, timeout=30,
    )
    lines = [l for l in result.stdout.strip().split("\n") if l and SERVICE_NAME in l]
    return len(lines)


def scale(replicas: int):
    logger.info("Scaling %s to %d replicas", SERVICE_NAME, replicas)
    subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, "up", "--scale", f"{SERVICE_NAME}={replicas}", "-d", "--no-deps", SERVICE_NAME],
        check=True, capture_output=True, text=True, timeout=120,
    )
    logger.info("Scale to %d complete", replicas)


def query_prometheus(query: str) -> float:
    resp = httpx.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}, timeout=10)
    resp.raise_for_status()
    data = resp.json()["data"]["result"]
    if data:
        return float(data[0]["value"][1])
    return 0.0


def evaluate(replicas: int):
    cpu = query_prometheus('rate(app_process_cpu_seconds_total[2m])')
    latency_raw = query_prometheus('sli:read_latency_p95:5m')
    latency = latency_raw if latency_raw > 0 else 0.0
    req_rate = query_prometheus('rate(http_requests_total[1m])')
    req_per_instance = req_rate / max(replicas, 1)

    logger.info(
        "Metrics — cpu=%.2f latency=%.3fs req/s=%.1f replicas=%d",
        cpu, latency, req_per_instance, replicas,
    )

    scale_up_reasons = []
    if cpu > SCALE_UP_THRESHOLD:
        scale_up_reasons.append(f"cpu={cpu:.2f} > {SCALE_UP_THRESHOLD}")
    if latency > P95_LATENCY_THRESHOLD:
        scale_up_reasons.append(f"latency={latency:.3f}s > {P95_LATENCY_THRESHOLD}s")
    if req_per_instance > REQUEST_RATE_THRESHOLD:
        scale_up_reasons.append(f"req/s={req_per_instance:.1f} > {REQUEST_RATE_THRESHOLD}")

    scale_down_reasons = []
    if cpu < SCALE_DOWN_THRESHOLD:
        scale_down_reasons.append(f"cpu={cpu:.2f} < {SCALE_DOWN_THRESHOLD}")
    if latency < P95_LATENCY_THRESHOLD * 0.5:
        scale_down_reasons.append(f"latency={latency:.3f}s < {P95_LATENCY_THRESHOLD * 0.5}s")

    should_scale_up = len(scale_up_reasons) >= 1
    should_scale_down = len(scale_down_reasons) >= 2 and not should_scale_up

    if should_scale_up:
        logger.info("Scale-up triggered: %s", "; ".join(scale_up_reasons))
    if should_scale_down:
        logger.info("Scale-down candidate: %s", "; ".join(scale_down_reasons))

    return should_scale_up, should_scale_down


def main():
    start_http_server(METRICS_PORT)
    logger.info("Autoscaler started — prometheus=%s service=%s min=%d max=%d poll=%ds cooldown=%ds",
                PROMETHEUS_URL, SERVICE_NAME, MIN_REPLICAS, MAX_REPLICAS, POLL_INTERVAL, COOLDOWN_SECONDS)

    last_scale_time = 0.0

    while True:
        try:
            current = get_current_replicas()
            replicas_current.set(current)

            should_scale_up, should_scale_down = evaluate(current)
            now = time.time()
            cooldown_remaining = COOLDOWN_SECONDS - (now - last_scale_time)
            desired = current

            if should_scale_up and current < MAX_REPLICAS and cooldown_remaining <= 0:
                desired = current + 1
                scale(desired)
                scale_up_events.inc()
                last_scale_time = time.time()
            elif should_scale_down and current > MIN_REPLICAS and cooldown_remaining <= 0:
                desired = current - 1
                scale(desired)
                scale_down_events.inc()
                last_scale_time = time.time()
            else:
                if (should_scale_up or should_scale_down) and cooldown_remaining > 0:
                    logger.debug("Cooldown active — %.0fs remaining", cooldown_remaining)

            replicas_desired.set(desired)
            last_evaluation.set_to_current_time()
        except httpx.RequestError as e:
            logger.warning("Prometheus query failed: %s", e)
        except subprocess.CalledProcessError as e:
            logger.error("Docker command failed: %s — stderr: %s", e, e.stderr)
        except Exception as e:
            logger.exception("Unexpected error in autoscaler loop: %s", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
