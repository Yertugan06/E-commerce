from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


async def get_active_connection_count() -> int:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND datname = current_database()")
        )
        return result.scalar() or 0
