from prometheus_client import REGISTRY
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, HistogramMetricFamily


def _get_counter_value(name: str, labels: dict[str, str] | None = None) -> float | None:
    val = REGISTRY.get_sample_value(name, labels)
    return val if val is not None else None


def _get_gauge_value(name: str, labels: dict[str, str] | None = None) -> float | None:
    val = REGISTRY.get_sample_value(name, labels)
    return val if val is not None else None


def _compute_p95_seconds(metric_name: str, labels: dict[str, str] | None = None) -> float | None:
    count = REGISTRY.get_sample_value(f"{metric_name}_count", labels)
    if count is None or count == 0:
        return None
    metric = REGISTRY.get_sample_value(f"{metric_name}_bucket", {**(labels or {}), "le": "+Inf"})
    if metric is None:
        return None
    total = count
    target = total * 0.95
    cumulative = 0.0
    prev_bound = 0.0
    for metric_family in REGISTRY.collect():
        if metric_family.name == metric_name:
            for sample in metric_family.samples:
                if sample.name == f"{metric_name}_bucket":
                    sample_labels = dict(sample.labels)
                    if labels:
                        for k, v in labels.items():
                            if sample_labels.get(k) != v:
                                break
                    else:
                        le = float(sample_labels.get("le", "+inf"))
                        cumulative += sample.value
                        if cumulative >= target:
                            if cumulative == 0:
                                return prev_bound
                            fraction = (target - (cumulative - sample.value)) / sample.value
                            return prev_bound + (le - prev_bound) * fraction
                        prev_bound = le
    return None


def _count_samples_by_label(
    metric_name: str,
    sample_name: str,
    label_key: str,
) -> dict[str, float]:
    result: dict[str, float] = {}
    for metric_family in REGISTRY.collect():
        if metric_family.name == metric_name:
            for sample in metric_family.samples:
                if sample.name == sample_name:
                    key = sample.labels.get(label_key, "unknown")
                    result[key] = result.get(key, 0) + sample.value
    return result


def _sum_counter_by_label(
    metric_name: str,
    label_key: str,
) -> dict[str, float]:
    return _count_samples_by_label(metric_name, f"{metric_name}_total", label_key)


def aggregate_health_dashboard() -> dict:
    result: dict = {}

    http_by_status = _sum_counter_by_label("http_requests_total", "status_group")
    total_reqs = sum(http_by_status.values()) if http_by_status else 0
    error_5xx = http_by_status.get("5xx", 0) if http_by_status else 0

    if total_reqs > 0:
        result["api_availability"] = {
            "total_requests": int(total_reqs),
            "success_rate": round(1.0 - (error_5xx / total_reqs), 4),
        }
        result["error_rate_5xx"] = {
            "count": int(error_5xx),
            "rate": round(error_5xx / total_reqs, 4),
        }
    else:
        result["api_availability"] = None
        result["error_rate_5xx"] = None

    db_available = _get_gauge_value("db_available")
    active_conns = _get_gauge_value("db_connections_active")
    result["database"] = (
        {
            "available": int(db_available),
            "active_connections": int(active_conns) if active_conns is not None else None,
        }
        if db_available is not None
        else None
    )

    latency: dict[str, float | None] = {}
    latency["read_p95_ms"] = _compute_p95_seconds(
        "http_request_duration_seconds", {"endpoint_group": "auth"}
    )
    latency["write_p95_ms"] = _compute_p95_seconds(
        "http_request_duration_seconds", {"endpoint_group": "checkout"}
    )
    latency["auth_p95_ms"] = _compute_p95_seconds(
        "http_request_duration_seconds", {"endpoint_group": "auth"}
    )
    for key in ("read_p95_ms", "write_p95_ms", "auth_p95_ms"):
        if latency[key] is not None:
            latency[key] = round(latency[key] * 1000, 2)
    result["latency"] = latency if any(v is not None for v in latency.values()) else None

    vol_by_status = _sum_counter_by_label("http_requests_total", "status_group")
    if vol_by_status:
        result["request_volume"] = {
            "2xx": int(vol_by_status.get("2xx", 0)),
            "4xx": int(vol_by_status.get("4xx", 0)),
            "5xx": int(vol_by_status.get("5xx", 0)),
            "total": int(sum(vol_by_status.values())),
        }
    else:
        result["request_volume"] = None

    checkout_by_status = _sum_counter_by_label("checkout_total", "status")
    checkout_success = checkout_by_status.get("success", 0) if checkout_by_status else 0
    checkout_failure = checkout_by_status.get("failure", 0) if checkout_by_status else 0
    checkout_total = checkout_success + checkout_failure
    if checkout_by_status:
        result["checkout"] = {
            "success_rate": round(checkout_success / checkout_total, 4) if checkout_total > 0 else 0,
            "duration_p95_ms": (
                round(v * 1000, 2)
                if (v := _compute_p95_seconds("checkout_duration_seconds")) is not None
                else None
            ),
            "by_status": {
                "success": int(checkout_success),
                "failure": int(checkout_failure),
            },
        }
    else:
        result["checkout"] = None

    order_vals = _count_samples_by_label(
        "order_persistence_validations_total",
        "order_persistence_validations_total",
        "status",
    )
    cart_vals = _count_samples_by_label(
        "cart_consistency_validations_total",
        "cart_consistency_validations_total",
        "status",
    )
    result["sli_validations"] = {
        "order_persistence_errors": int(order_vals.get("failure", 0)) if order_vals else 0,
        "cart_consistency_errors": int(cart_vals.get("failure", 0)) if cart_vals else 0,
    }

    mem = _get_gauge_value("app_process_resident_memory_bytes")
    cpu = _get_gauge_value("app_process_cpu_seconds_total")
    result["process"] = {
        "memory_bytes": int(mem) if mem is not None else None,
        "cpu_seconds_total": round(cpu, 2) if cpu is not None else None,
    }

    return result
