from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import AppError
from app.models.enums import RequestStatus
from app.models.maintenance_request import MaintenanceRequest
from app.services.maintenance_request import MaintenanceRequestService


@pytest.mark.asyncio
async def test_service_rejects_new_to_completed_transition() -> None:
    session = AsyncMock()
    service = MaintenanceRequestService(session, notification_task=AsyncMock())
    item = MaintenanceRequest(
        id=1,
        equipment_id=1,
        requester_id=1,
        assignee_id=2,
        status=RequestStatus.NEW,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with pytest.raises(AppError) as exc:
        service._validate_transition(item, RequestStatus.COMPLETED, {})

    assert exc.value.code == "INVALID_STATUS_TRANSITION"


@pytest.mark.asyncio
async def test_service_requires_assignee_for_forward_transition() -> None:
    service = MaintenanceRequestService(MagicMock(), notification_task=AsyncMock())
    item = MaintenanceRequest(
        id=1,
        equipment_id=1,
        requester_id=1,
        assignee_id=None,
        status=RequestStatus.NEW,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with pytest.raises(AppError) as exc:
        service._validate_transition(item, RequestStatus.ASSIGNED, {})

    assert exc.value.code == "ASSIGNEE_REQUIRED"
