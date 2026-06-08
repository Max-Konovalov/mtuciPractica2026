from __future__ import annotations

from app.models.notification_log import NotificationLog
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[NotificationLog]):
    model = NotificationLog
