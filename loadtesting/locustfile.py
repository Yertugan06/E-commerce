import os
import random

from locust import HttpUser, task, between

PRODUCT_IDS = [int(x) for x in os.getenv("PRODUCT_IDS", "101,102,103,104,105").split(",")]


class ECommerceUser(HttpUser):
    wait_time = between(1.0, 3.0)

    def on_start(self):
        email = f"locust_{hash(self)}_{random.randint(10000, 99999)}@test.com"
        password = "TestPass123!"

        r = self.client.post("/auth/register", json={"email": email, "password": password})
        if r.status_code == 201:
            self.token = None
            r2 = self.client.post("/auth/login", json={"email": email, "password": password})
            if r2.status_code == 200:
                self.token = r2.json().get("access_token", "")
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.token = None
        elif r.status_code == 409:
            r2 = self.client.post("/auth/login", json={"email": email, "password": password})
            if r2.status_code == 200:
                self.token = r2.json().get("access_token", "")
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.token = None
        else:
            self.token = None

    @task(3)
    def browse_health(self):
        self.client.get("/health", name="/health")

    @task(5)
    def browse_root(self):
        self.client.get("/", name="/")

    @task(2)
    def browse_nonexistent(self):
        self.client.get("/nonexistent", name="/nonexistent (404)")

    @task(10)
    def browse_me(self):
        if self.token:
            self.client.get("/auth/me", headers=self.headers, name="/auth/me")

    @task(8)
    def add_cart_item(self):
        if self.token:
            pid = random.choice(PRODUCT_IDS)
            qty = random.randint(1, 3)
            self.client.post(
                "/cart/items",
                json={"product_id": pid, "quantity": qty},
                headers=self.headers,
                name="/cart/items [POST]",
            )

    @task(4)
    def checkout(self):
        if self.token:
            self.client.post("/checkout", headers=self.headers, name="/checkout")

    @task(6)
    def list_orders(self):
        if self.token:
            self.client.get("/orders", headers=self.headers, name="/orders")

    @task(3)
    def random_nonexistent(self):
        self.client.get(f"/random-{random.randint(1000, 9999)}", name="/random-404")
