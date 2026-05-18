import logging
import os
import time

import docker
import httpx
from prometheus_client import Counter, Gauge, start_http_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("autoscaler")

PROMETHEUS_URL = os.getenv("AUTOSCALER_PROMETHEUS_URL", "http://prometheus:9090")
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

AUTOSCALER_LABEL = "com.ecommerce.autoscaler"

docker_client = docker.from_env()

replicas_current = Gauge("autoscaler_replicas_current", "Current number of backend replicas")
replicas_desired = Gauge("autoscaler_replicas_desired", "Desired number of backend replicas")
replicas_min = Gauge("autoscaler_replicas_min", "Minimum allowed replicas")
replicas_max = Gauge("autoscaler_replicas_max", "Maximum allowed replicas")
scale_up_events = Counter("autoscaler_scale_up_events_total", "Total scale-up events")
scale_down_events = Counter("autoscaler_scale_down_events_total", "Total scale-down events")
last_evaluation = Gauge("autoscaler_last_evaluation_seconds", "Timestamp of last evaluation")

replicas_min.set(MIN_REPLICAS)
replicas_max.set(MAX_REPLICAS)


def _get_backend_containers():
    return docker_client.containers.list(
        all=False,
        filters={"label": f"{AUTOSCALER_LABEL}={SERVICE_NAME}"},
    )


def get_current_replicas() -> int:
    return len(_get_backend_containers())


def scale(replicas: int):
    current = get_current_replicas()
    logger.info("Scaling %s to %d replicas (currently %d)", SERVICE_NAME, replicas, current)

    if replicas > current:
        _scale_up(replicas - current)
    elif replicas < current:
        _scale_down(current - replicas)


def _scale_up(count: int):
    existing = _get_backend_containers()
    if not existing:
        logger.error("No %s containers found to use as template", SERVICE_NAME)
        return
    template = existing[0].attrs
    template_container = existing[0]

    img = template["Config"]["Image"]
    env = template["Config"].get("Env", [])
    network_name = next(iter(template["NetworkSettings"]["Networks"].keys()))
    prefix = template_container.name.rsplit("-", 1)[0]

    for _ in range(count):
        all_names = {c.name for c in docker_client.containers.list(all=True)}
        idx = 0
        while f"{prefix}-{idx}" in all_names:
            idx += 1
        new_name = f"{prefix}-{idx}"

        container = docker_client.containers.create(
            image=img,
            name=new_name,
            environment=env,
            labels={AUTOSCALER_LABEL: SERVICE_NAME},
        )

        network = docker_client.networks.get(network_name)
        network.connect(container, aliases=[SERVICE_NAME])
        container.start()
        logger.info("Created and started %s", new_name)


def _scale_down(count: int):
    containers = sorted(
        _get_backend_containers(),
        key=lambda c: c.name,
        reverse=True,
    )
    for c in containers[:count]:
        logger.info("Stopping and removing %s", c.name)
        c.stop(timeout=10)
        c.remove()


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
        except docker.errors.APIError as e:
            logger.error("Docker API error: %s", e)
        except Exception as e:
            logger.exception("Unexpected error in autoscaler loop: %s", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
