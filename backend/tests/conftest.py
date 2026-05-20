import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from sqlalchemy import text

from app.core.config import settings
from app.core.database import SQLModel, get_session
from app.features.products.models import Product
from app.main import app

test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)


@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(test_engine) as session:
        for i in range(1, 200):
            session.add(Product(id=i, name=f"Product {i}", price=10.0, stock=100))
        await session.commit()
        await session.execute(text("SELECT setval('products_id_seq', 199)"))

    async def override_get_session():
        async with AsyncSession(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    email = "test@example.com"
    password = "testpass123"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def second_user_headers(client: AsyncClient) -> dict:
    email = "other@example.com"
    password = "testpass123"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
