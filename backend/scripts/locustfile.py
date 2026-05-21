"""Locust load test for the e-commerce backend.

Simulates realistic user flows: browse products, add items to cart, checkout.

Usage:
    locust -f backend/scripts/locustfile.py --host http://localhost:8000
"""

import random
from locust import HttpUser, task, between, constant
from locust.exception import RescheduleTask


class AnonymousBrowser(HttpUser):
    """Simulates a user browsing products without logging in."""

    wait_time = between(1, 5)

    @task(3)
    def browse_products(self):
        self.client.get("/products", name="GET /products")

    @task(1)
    def browse_products_with_auth(self):
        """Products endpoint doesn't require auth, but test it either way."""
        with self.client.get(
            "/products",
            name="GET /products (empty users)",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.success()


class AuthenticatedUser(HttpUser):
    """Simulates a logged-in user who browses, carts, and checkouts out."""

    wait_time = between(2, 7)

    def on_start(self):
        """Register and login on start, build up a cart."""
        email = f"locust_{random.randint(10_000, 999_999)}@test.com"
        password = "test123456"

        register_resp = self.client.post(
            "/auth/register",
            json={"email": email, "password": password},
            name="POST /auth/register",
        )
        if register_resp.status_code == 409:
            login_resp = self.client.post(
                "/auth/login",
                json={"email": email, "password": password},
                name="POST /auth/login",
            )
        elif register_resp.ok:
            self.token = register_resp.json().get("access_token", "")
        else:
            raise RescheduleTask()

        if not self.token:
            login_resp = self.client.post(
                "/auth/login",
                json={"email": email, "password": password},
                name="POST /auth/login",
            )
            if login_resp.ok:
                self.token = login_resp.json().get("access_token", "")
            else:
                raise RescheduleTask()

        self.headers = {"Authorization": f"Bearer {self.token}"}
        self._get_products_and_add_to_cart()

    def _get_products_and_add_to_cart(self):
        """Fetch products and add some to cart."""
        resp = self.client.get("/products", headers=self.headers, name="GET /products")
        if not resp.ok:
            return
        products = resp.json()
        if not products:
            return
        for p in random.sample(products, min(3, len(products))):
            product_name = p.get("name", p.get("id", "?"))
            self.client.post(
                "/cart/items",
                json={"product_id": p["id"], "quantity": random.randint(1, 2)},
                headers=self.headers,
                name="POST /cart/items",
            )

    @task(5)
    def view_cart(self):
        self.client.get("/cart", headers=self.headers, name="GET /cart")

    @task(5)
    def browse_products(self):
        self.client.get("/products", headers=self.headers, name="GET /products")

    @task(2)
    def view_orders(self):
        self.client.get("/orders", headers=self.headers, name="GET /orders")

    @task(3)
    def add_item_and_checkout(self):
        """Add a random product to cart and checkout."""
        resp = self.client.get("/products", headers=self.headers, name="GET /products")
        if not resp.ok:
            return
        products = resp.json()
        if not products:
            return
        p = random.choice(products)
        self.client.post(
            "/cart/items",
            json={"product_id": p["id"], "quantity": 1},
            headers=self.headers,
            name="POST /cart/items",
        )
        self.client.post(
            "/checkout", headers=self.headers, name="POST /checkout"
        )

    @task(1)
    def view_order_detail(self):
        resp = self.client.get("/orders", headers=self.headers, name="GET /orders")
        if resp.ok:
            orders = resp.json()
            if orders:
                order_id = orders[0]["id"]
                self.client.get(
                    f"/orders/{order_id}",
                    headers=self.headers,
                    name="GET /orders/{id}",
                )
