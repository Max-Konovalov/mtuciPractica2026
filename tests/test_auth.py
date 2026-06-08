from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_is_public(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_key_required(client: AsyncClient) -> None:
    response = await client.get("/equipment")
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_invalid_api_key_rejected(client: AsyncClient) -> None:
    response = await client.get("/equipment", headers={"X-API-Key": "bad"})
    assert response.status_code == 401
