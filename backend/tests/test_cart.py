import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestCart:
    async def test_get_empty_cart(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/cart", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    async def test_add_item(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/cart/items",
            json={"product_id": 1, "quantity": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["product_id"] == 1
        assert resp.json()["quantity"] == 2

    async def test_add_duplicate_product(self, client: AsyncClient, auth_headers: dict):
        await client.post(
            "/cart/items",
            json={"product_id": 99, "quantity": 1},
            headers=auth_headers,
        )
        resp = await client.post(
            "/cart/items",
            json={"product_id": 99, "quantity": 1},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "RESOURCE_CONFLICT"

    async def test_update_quantity(self, client: AsyncClient, auth_headers: dict):
        add_resp = await client.post(
            "/cart/items",
            json={"product_id": 50, "quantity": 1},
            headers=auth_headers,
        )
        item_id = add_resp.json()["id"]
        resp = await client.put(
            f"/cart/items/{item_id}",
            json={"quantity": 5},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["quantity"] == 5

    async def test_remove_item(self, client: AsyncClient, auth_headers: dict):
        add_resp = await client.post(
            "/cart/items",
            json={"product_id": 77, "quantity": 1},
            headers=auth_headers,
        )
        item_id = add_resp.json()["id"]
        resp = await client.delete(f"/cart/items/{item_id}", headers=auth_headers)
        assert resp.status_code == 204

        cart = await client.get("/cart", headers=auth_headers)
        assert all(i["product_id"] != 77 for i in cart.json()["items"])

    async def test_cart_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/cart")
        assert resp.status_code == 401
