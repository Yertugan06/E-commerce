import pytest
from httpx import ASGITransport, AsyncClient


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


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "app_process_cpu_seconds_total" in body
    assert "app_process_resident_memory_bytes" in body


@pytest.mark.asyncio
async def test_sli_middleware_records_metrics(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200

    metrics_resp = await client.get("/metrics")
    assert metrics_resp.status_code == 200
    body = metrics_resp.text

    assert 'http_requests_total{method="GET",path="other",status_group="2xx"}' in body
