"""
Generate synthetic API traffic to populate all 11 SLI metrics in Prometheus.

Usage:
    uv run python -m scripts.generate_sli_traffic

Requires:
    - Backend running at http://localhost:8000
    - httpx package (available in test deps)
"""

import asyncio
import sys
import time

import httpx

BASE = "http://localhost:8000"
PASSWORD = "TestPass123!"
CYCLES = 5


async def generate_traffic():
    async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
        print(f"Generating SLI traffic against {BASE} ({CYCLES} cycles)...")
        start = time.monotonic()

        for cycle in range(1, CYCLES + 1):
            print(f"\n--- Cycle {cycle}/{CYCLES} ---")
            user_email = f"sli_user_{cycle}@test.com"

            # Phase 1: Auth — register, login, /me
            print("  Auth: register...", end=" ")
            r = await client.post("/auth/register", json={"email": user_email, "password": PASSWORD})
            print(f"{r.status_code}", end="")

            print("  login...", end=" ")
            r = await client.post("/auth/login", json={"email": user_email, "password": PASSWORD})
            print(f"{r.status_code}", end="")
            token = r.json().get("access_token", "")
            headers = {"Authorization": f"Bearer {token}"}

            print("  /me...", end=" ")
            r = await client.get("/auth/me", headers=headers)
            print(f"{r.status_code}")

            # Phase 2: Cart — add items
            print("  Cart: add items...", end=" ")
            item_ids = []
            for pid in [101, 102, 103]:
                r = await client.post("/cart/items", json={"product_id": pid, "quantity": cycle}, headers=headers)
                print(f"{r.status_code}", end="")
                if r.status_code == 201:
                    item_ids.append(r.json()["id"])
            print()

            # Phase 2b: Cart — update first item
            if item_ids:
                print(f"  Cart: update item {item_ids[0]}...", end=" ")
                r = await client.put(f"/cart/items/{item_ids[0]}", json={"quantity": 5}, headers=headers)
                print(f"{r.status_code}")

                print(f"  Cart: delete last item...", end=" ")
                r = await client.delete(f"/cart/items/{item_ids[-1]}", headers=headers)
                print(f"{r.status_code}")

                print("  Cart: add replacement item...", end=" ")
                r = await client.post("/cart/items", json={"product_id": 104, "quantity": 1}, headers=headers)
                print(f"{r.status_code}")

                # Re-add the deleted product so checkout has items
                print("  Cart: re-add for checkout...", end=" ")
                r = await client.post("/cart/items", json={"product_id": 105, "quantity": 2}, headers=headers)
                print(f"{r.status_code}")

            # Phase 3: Checkout — success (has items), then failure (empty cart)
            print("  Checkout: success...", end=" ")
            r = await client.post("/checkout", headers=headers)
            print(f"{r.status_code}", end="")
            order_id = None
            if r.status_code == 200:
                order_id = r.json()["id"]

            print("  failure (empty cart)...", end=" ")
            r = await client.post("/checkout", headers=headers)
            print(f"{r.status_code}")

            # Phase 4: Orders — list and detail
            print("  Orders: list...", end=" ")
            r = await client.get("/orders", headers=headers)
            print(f"{r.status_code}", end="")
            orders = r.json()
            if orders:
                oid = orders[0]["id"]
                print(f"  detail {oid}...", end=" ")
                r = await client.get(f"/orders/{oid}", headers=headers)
                print(f"{r.status_code}")
            else:
                print()

            # Phase 5: Health + 404
            print("  Health...", end=" ")
            r = await client.get("/health")
            print(f"{r.status_code}", end="")

            print("  404...", end=" ")
            r = await client.get("/nonexistent")
            print(f"{r.status_code}")

            # Brief pause so endpoints aren't hammered
            await asyncio.sleep(0.1)

        elapsed = time.monotonic() - start
        print(f"\nDone. Generated {CYCLES} cycles of traffic in {elapsed:.1f}s")
        print(f"Prometheus scrapes every 15s — refresh the Grafana dashboard after ~30s.")


if __name__ == "__main__":
    asyncio.run(generate_traffic())
