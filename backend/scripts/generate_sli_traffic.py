"""
Generate synthetic API traffic to populate all SLI metrics in Prometheus.

Usage:
    uv run python -m scripts.generate_sli_traffic

Requires:
    - Backend running at http://localhost:8000
    - Products seeded (run seed.py first)
    - httpx package (available in test deps)
"""

import asyncio
import random
import time

import httpx

BASE = "http://localhost:8000"
PASSWORD = "TestPass123!"
CYCLES = 500
FAILURE_RATE = 0.05


async def generate_traffic():
    async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
        print(f"Generating SLI traffic against {BASE} ({CYCLES} cycles, ~{FAILURE_RATE*100:.0f}% failure rate)...")
        start = time.monotonic()
        total_requests = 0

        for cycle in range(1, CYCLES + 1):
            user_email = f"sli_user_{cycle}@test.com"

            delay = random.uniform(0.01, 0.15)
            await asyncio.sleep(delay)

            r = await client.post("/auth/register", json={"email": user_email, "password": PASSWORD})
            total_requests += 1

            r = await client.post("/auth/login", json={"email": user_email, "password": PASSWORD})
            total_requests += 1
            token = r.json().get("access_token", "")
            headers = {"Authorization": f"Bearer {token}"}

            r = await client.get("/auth/me", headers=headers)
            total_requests += 1

            pid = random.choice([1, 2, 3, 4])
            r = await client.post("/cart/items", json={"product_id": pid, "quantity": random.randint(1, 3)}, headers=headers)
            total_requests += 1
            item_id = r.json().get("id") if r.status_code == 201 else None

            if item_id and random.random() < 0.3:
                r = await client.put(f"/cart/items/{item_id}", json={"quantity": random.randint(1, 5)}, headers=headers)
                total_requests += 1

            if random.random() < FAILURE_RATE:
                r = await client.get(f"/cart/items/999999", headers=headers)
                total_requests += 1

            if random.random() < FAILURE_RATE:
                r = await client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
                total_requests += 1

            if random.random() < FAILURE_RATE:
                r = await client.post("/checkout", headers=headers)
                total_requests += 1

            r = await client.post("/checkout", headers=headers)
            total_requests += 1

            r = await client.get("/orders", headers=headers)
            total_requests += 1
            orders = r.json()
            if orders:
                oid = orders[0]["id"]
                r = await client.get(f"/orders/{oid}", headers=headers)
                total_requests += 1

            if random.random() < FAILURE_RATE:
                r = await client.get("/nonexistent", headers=headers)
                total_requests += 1

            if random.random() < FAILURE_RATE:
                r = await client.post("/cart/items", json={"product_id": 999, "quantity": 1}, headers=headers)
                total_requests += 1

            if cycle % 50 == 0:
                elapsed = time.monotonic() - start
                rate = total_requests / elapsed if elapsed > 0 else 0
                print(f"  Cycle {cycle}/{CYCLES} — {total_requests} reqs in {elapsed:.0f}s ({rate:.1f} req/s)")

        elapsed = time.monotonic() - start
        print(f"\nDone. {total_requests} requests in {elapsed:.1f}s ({total_requests/elapsed:.1f} req/s)")
        print(f"Prometheus scrapes every 5s — refresh the Grafana dashboard after ~15s.")


if __name__ == "__main__":
    asyncio.run(generate_traffic())
