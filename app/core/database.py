from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_sessionmaker()() as session:
        yield session


async def init_database_if_sqlite() -> None:
    settings = get_settings()
    if not settings.database_url.startswith("sqlite+aiosqlite"):
        return

    import app.models  # noqa: F401

    maker = get_sessionmaker()
    async with maker() as session:
        async with session.bind.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
