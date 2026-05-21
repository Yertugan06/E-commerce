#!/usr/bin/env python3
"""Auto-scaler for Docker Compose backend.

Polls container CPU/memory via docker stats and scales the backend service
in/out: CPU > 60% → scale up, memory > 500 MB → scale up, with cooldown.

Usage:
  python scripts/autoscale.sh      # run from repo root
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone

# ── Thresholds ─────────────────────────────────────────────────────────
CPU_SCALE_UP = 60.0       # % — scale up if avg CPU exceeds this
CPU_SCALE_DOWN = 20.0     # % — scale down if avg CPU below this
MEM_SCALE_UP_MB = 500     # MB — scale up if avg RSS exceeds this
MEM_SCALE_DOWN_MB = 200   # MB — scale down if avg RSS below this
MIN_REPLICAS = 1
MAX_REPLICAS = 10
CHECK_INTERVAL = 15       # seconds
COOLDOWN_UP = 30          # seconds — react quickly to spikes
COOLDOWN_DOWN = 120       # seconds — slow to scale back, avoids oscillation
SUSTAINED_CHECKS = 2      # scale up only after N consecutive breaches


def _run(cmd: list[str], *, check: bool = True) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"  ⚠ cmd failed (code {r.returncode}): {' '.join(cmd)}")
        if r.stderr.strip():
            for line in r.stderr.strip().split("\n"):
                print(f"    stderr: {line}")
    return r.stdout.strip()


def backend_containers() -> list[str]:
    """Return container IDs of current backend replicas.

    Works with both Docker Compose and Terraform-managed containers
    (named ecommerce-backend-0, ecommerce-backend-1, ...).
    """
    out = _run(["docker", "compose", "ps", "-q", "backend"])
    ids = [c for c in out.split("\n") if c]
    if ids:
        return ids
    # Fallback: Terraform-style naming
    out = _run(["docker", "ps", "-q", "--filter", "name=ecommerce-backend"])
    return [c for c in out.split("\n") if c]


def container_stats(container_id: str) -> dict | None:
    """docker stats for a single container, parsed from JSON."""
    out = _run([
        "docker", "stats", "--no-stream", "--format", "{{json .}}",
        container_id,
    ])
    if not out:
        return None
    return json.loads(out)


def parse_mem_mb(mem_usage: str) -> float:
    """'123.4MiB / 15.6GiB' → used portion in MB."""
    used = mem_usage.split("/")[0].strip()
    if "GiB" in used:
        return float(used.replace("GiB", "")) * 1024
    if "MiB" in used:
        return float(used.replace("MiB", ""))
    if "KiB" in used:
        return float(used.replace("KiB", "")) / 1024
    return 0.0


def current_replicas() -> int:
    return len(backend_containers())


def scale_to(target: int) -> None:
    """Scale backend to target replicas.

    Works with Docker Compose (docker compose up --scale) and Terraform
    (creates/removes containers with docker run / docker rm).
    """
    current = current_replicas()
    if current == target:
        return

    if target > current:
        # Scale up — create new replicas
        if _is_compose():
            print(f"  → docker compose up --scale backend={target} -d backend")
            _run(["docker", "compose", "up", "--scale", f"backend={target}", "-d", "backend"])
        else:
            _run_extra_replicas(target - current)
    else:
        # Scale down — remove newest replicas
        if _is_compose():
            print(f"  → docker compose up --scale backend={target} -d backend")
            _run(["docker", "compose", "up", "--scale", f"backend={target}", "-d", "backend"])
        else:
            _remove_extra_replicas(current - target)


def _is_compose() -> bool:
    """Check if the running backend is managed by Docker Compose."""
    out = _run(["docker", "compose", "ps", "-q", "backend"])
    return bool(out.strip())


def _run_extra_replicas(count: int) -> None:
    """Create N extra backend containers by cloning the first replica."""
    existing = _run(["docker", "ps", "--filter", "name=ecommerce-backend", "--format", "{{.Names}}"])
    names = [n for n in existing.split("\n") if n]
    if not names:
        return
    name = names[0]

    # Get the image used by the existing container
    image = _run(["docker", "inspect", name, "--format", "{{.Config.Image}}"])
    indices = [int(n.rsplit("-", 1)[-1]) for n in names if "-" in n]
    next_idx = max(indices) + 1 if indices else 1

    for i in range(count):
        new_name = f"ecommerce-backend-{next_idx + i}"
        # Skip if name already exists (e.g. managed by Terraform)
        existing_check = _run(["docker", "ps", "-a", "--filter", f"name=^{new_name}$", "--format", "{{.Names}}"], check=False)
        if new_name in existing_check:
            print(f"  ⚠ {new_name} already exists — skipping")
            continue
        print(f"  → docker run -d --name {new_name} (replica {next_idx + i})")
        _run([
            "docker", "run", "-d",
            "--name", new_name,
            "--network", "ecommerce-network",
            "--network-alias", "backend",
            "--restart", "unless-stopped",
            "-e", "DATABASE_URL=postgresql+asyncpg://postgres:postgres@ecommerce-postgres:5432/ecommerce",
            "-e", "SECRET_KEY=change-me-to-a-random-secret-key",
            "-e", "ALGORITHM=HS256",
            "-e", "ACCESS_TOKEN_EXPIRE_MINUTES=30",
            image,
        ])


def _remove_extra_replicas(count: int) -> None:
    """Remove the last N backend container replicas."""
    existing = _run(["docker", "ps", "--filter", "name=ecommerce-backend", "--format", "{{.Names}}"])
    names = sorted(n for n in existing.split("\n") if n)
    for name in names[-count:]:
        print(f"  → docker rm -f {name}")
        _run(["docker", "rm", "-f", name])


def main() -> None:
    print("=== Docker Compose Auto-Scaler ===")
    print(f"CPU  : up > {CPU_SCALE_UP:.0f}%  | down < {CPU_SCALE_DOWN:.0f}%")
    print(f"MEM  : up > {MEM_SCALE_UP_MB:.0f} MB | down < {MEM_SCALE_DOWN_MB:.0f} MB")
    print(f"Range: {MIN_REPLICAS}–{MAX_REPLICAS} replicas  | "
          f"cooldown up {COOLDOWN_UP}s / down {COOLDOWN_DOWN}s  | "
          f"sustained x{SUSTAINED_CHECKS}")
    print()

    last_scale_up = 0.0
    last_scale_down = 0.0
    breach_count = 0  # consecutive checks above scale-up threshold

    while True:
        containers = backend_containers()
        current = len(containers)

        if current == 0:
            print(f"[{datetime.now(timezone.utc).isoformat()}] "
                  f"No backend containers — is 'docker compose up' running?")
            breach_count = 0
            time.sleep(CHECK_INTERVAL)
            continue

        stats = []
        for cid in containers:
            s = container_stats(cid)
            if s:
                stats.append(s)

        if not stats:
            time.sleep(CHECK_INTERVAL)
            continue

        avg_cpu = sum(float(s["CPUPerc"].rstrip("%")) for s in stats) / len(stats)
        avg_mem = sum(parse_mem_mb(s["MemUsage"]) for s in stats) / len(stats)

        now = time.time()
        ts = datetime.now(timezone.utc).isoformat()

        # ── Decision ──────────────────────────────────────────────────
        new = current
        reason = ""

        # Scale-up check — must sustain N consecutive breaches
        if avg_cpu > CPU_SCALE_UP or avg_mem > MEM_SCALE_UP_MB:
            breach_count += 1
            condition = (f"CPU {avg_cpu:.1f}% > {CPU_SCALE_UP:.0f}%" if avg_cpu > CPU_SCALE_UP
                         else f"MEM {avg_mem:.0f} MB > {MEM_SCALE_UP_MB} MB")
            if breach_count >= SUSTAINED_CHECKS:
                new = current + 1
                reason = f"{condition} (sustained x{breach_count})"
            else:
                print(f"[{ts}] Spike {breach_count}/{SUSTAINED_CHECKS} — {condition}")
                time.sleep(CHECK_INTERVAL)
                continue
        else:
            breach_count = 0

            if avg_cpu < CPU_SCALE_DOWN and avg_mem < MEM_SCALE_DOWN_MB and current > MIN_REPLICAS:
                new = current - 1
                reason = (f"CPU {avg_cpu:.1f}% < {CPU_SCALE_DOWN:.0f}% and "
                          f"MEM {avg_mem:.0f} MB < {MEM_SCALE_DOWN_MB} MB")

        new = max(MIN_REPLICAS, min(MAX_REPLICAS, new))

        # ── Act ───────────────────────────────────────────────────────
        if new > current:
            if now - last_scale_up >= COOLDOWN_UP:
                print(f"[{ts}] Scaling {current} → {new}  ({reason})")
                scale_to(new)
                last_scale_up = now
            else:
                remain = int(COOLDOWN_UP - (now - last_scale_up))
                print(f"[{ts}] Hold scale-up ({reason}, cooldown {remain}s left)")
        elif new < current:
            if now - last_scale_down >= COOLDOWN_DOWN:
                print(f"[{ts}] Scaling {current} → {new}  ({reason})")
                scale_to(new)
                last_scale_down = now
            else:
                remain = int(COOLDOWN_DOWN - (now - last_scale_down))
                print(f"[{ts}] Hold scale-down ({reason}, cooldown {remain}s left)")
        else:
            print(f"[{ts}] {current} replicas  |  "
                  f"CPU {avg_cpu:.1f}%  |  MEM {avg_mem:.0f} MB")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAuto-scaler stopped.")
        sys.exit(0)
