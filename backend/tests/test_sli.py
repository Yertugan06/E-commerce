import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "version" in data
    if response.status_code == 200:
        assert data["status"] == "ok"
        assert data["database"]["status"] == "up"
