from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.errors import AppError


async def require_api_key(
    x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None,
    settings: Settings = Depends(get_settings),
) -> None:
    if not x_api_key or x_api_key != settings.api_key:
        raise AppError(status_code=401, detail="Invalid or missing API key", code="UNAUTHORIZED")
