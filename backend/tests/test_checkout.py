import pytest
from httpx import AsyncClient


@pytest.fixture
async def cart_with_items(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/cart/items",
        json={"product_id": 10, "quantity": 2},
        headers=auth_headers,
    )
    await client.post(
        "/cart/items",
        json={"product_id": 20, "quantity": 1},
        headers=auth_headers,
    )
    return auth_headers


class TestCheckout:
    async def test_checkout_success(self, client: AsyncClient, cart_with_items: dict):
        resp = await client.post("/checkout", headers=cart_with_items)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "confirmed"
        assert len(data["items"]) == 2

    async def test_checkout_empty_cart(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/checkout", headers=auth_headers)
        assert resp.status_code == 400

    async def test_cart_cleared_after_checkout(self, client: AsyncClient, cart_with_items: dict):
        await client.post("/checkout", headers=cart_with_items)
        cart = await client.get("/cart", headers=cart_with_items)
        assert cart.json()["items"] == []

    async def test_get_orders(self, client: AsyncClient, cart_with_items: dict):
        await client.post("/checkout", headers=cart_with_items)
        resp = await client.get("/orders", headers=cart_with_items)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_get_order_detail(self, client: AsyncClient, cart_with_items: dict):
        checkout_resp = await client.post("/checkout", headers=cart_with_items)
        order_id = checkout_resp.json()["id"]

        resp = await client.get(f"/orders/{order_id}", headers=cart_with_items)
        assert resp.status_code == 200
        assert resp.json()["id"] == order_id
        assert len(resp.json()["items"]) == 2

    async def test_get_other_users_order(
        self, client: AsyncClient, cart_with_items: dict, second_user_headers: dict
    ):
        checkout_resp = await client.post("/checkout", headers=cart_with_items)
        order_id = checkout_resp.json()["id"]

        resp = await client.get(f"/orders/{order_id}", headers=second_user_headers)
        assert resp.status_code == 404
