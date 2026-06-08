from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationChannel, NotificationStatus


class NotificationLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    channel: NotificationChannel
    status: NotificationStatus
    payload_json: dict[str, Any]
    created_at: datetime
