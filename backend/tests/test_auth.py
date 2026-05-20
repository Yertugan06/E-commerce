import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuthRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/auth/register",
            json={"email": "new@example.com", "password": "testpass123"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "new@example.com"

    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post(
            "/auth/register",
            json={"email": "dup@example.com", "password": "testpass123"},
        )
        resp = await client.post(
            "/auth/register",
            json={"email": "dup@example.com", "password": "testpass123"},
        )
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "RESOURCE_CONFLICT"

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post(
            "/auth/register",
            json={"email": "short@example.com", "password": "12345"},
        )
        assert resp.status_code == 422
        assert resp.json()["error_code"] == "VALIDATION_ERROR"


class TestAuthLogin:
    async def test_login_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/auth/register",
            json={"email": "wrongpw@example.com", "password": "testpass123"},
        )
        resp = await client.post(
            "/auth/login",
            json={"email": "wrongpw@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401
        assert resp.json()["error_code"] == "AUTH_INVALID_CREDENTIALS"

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "testpass123"},
        )
        assert resp.status_code == 401


class TestAuthMe:
    async def test_me_authenticated(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    async def test_me_no_token(self, client: AsyncClient):
        resp = await client.get("/auth/me")
        assert resp.status_code == 401
