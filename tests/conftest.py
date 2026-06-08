from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from app.core.database import get_db_session, get_sessionmaker
from app.main import create_app

TEST_API_KEY = "test-api-key"


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL for integration tests")
    return url


@pytest.fixture(scope="session")
def override_settings(test_database_url: str) -> None:
    get_settings.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["API_KEY"] = TEST_API_KEY
    os.environ["DATABASE_URL"] = test_database_url
    os.environ["CORS_ORIGINS"] = "http://localhost,http://localhost:8000"


@pytest.fixture(scope="session")
def migrated_db(test_database_url: str, override_settings: None) -> None:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", test_database_url)
    command.downgrade(config, "base")
    command.upgrade(config, "head")


@pytest.fixture
async def session(test_database_url: str, migrated_db: None) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(test_database_url, echo=False)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db_session:
        yield db_session
        await db_session.rollback()
    await engine.dispose()


@pytest.fixture
async def client(test_database_url: str, migrated_db: None) -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(test_database_url, echo=False)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        async with maker() as db_session:
            yield db_session

    app = create_app()
    app.dependency_overrides[get_db_session] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as api_client:
        yield api_client
    await engine.dispose()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}
