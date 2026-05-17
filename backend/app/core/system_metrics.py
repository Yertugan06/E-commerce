import os

from prometheus_client import Gauge

from app.core.config import settings

process_cpu_seconds_total = Gauge(
    "app_process_cpu_seconds_total",
    "Total user and system CPU time spent in seconds",
)

process_resident_memory_bytes = Gauge(
    "app_process_resident_memory_bytes",
    "Resident memory size in bytes",
)


def collect_process_metrics():
    if not settings.SLI_ENABLED:
        return

    try:
        import psutil
        process = psutil.Process()
        cpu_time = process.cpu_times()
        process_cpu_seconds_total.set(cpu_time.user + cpu_time.system)
        process_resident_memory_bytes.set(process.memory_info().rss)
    except ImportError:
        pass
    except Exception:
        pass
