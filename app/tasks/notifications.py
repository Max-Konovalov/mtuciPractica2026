from __future__ import annotations

import asyncio
import random

from app.core.database import get_sessionmaker
from app.core.logging import logger
from app.models.enums import NotificationChannel, NotificationStatus
from app.repositories.notification import NotificationRepository


async def send_notification_stub(request_id: int, event: str) -> None:
    await asyncio.sleep(random.uniform(0.5, 1.0))
    payload = {"request_id": request_id, "event": event, "message": f"Maintenance request {event}"}
    logger.info("notification_sent", payload=payload)
    async with get_sessionmaker()() as session:
        repo = NotificationRepository(session)
        await repo.create(
            {
                "request_id": request_id,
                "channel": NotificationChannel.INTERNAL,
                "status": NotificationStatus.SENT,
                "payload_json": payload,
            }
        )
        await session.commit()
