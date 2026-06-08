from __future__ import annotations

from datetime import datetime, timezone
from typing import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.enums import RequestPriority, RequestStatus
from app.models.maintenance_request import MaintenanceRequest
from app.repositories.employee import EmployeeRepository
from app.repositories.equipment import EquipmentRepository
from app.repositories.maintenance_request import MaintenanceRequestRepository
from app.schemas.maintenance_request import MaintenanceRequestCreate, MaintenanceRequestUpdate
from app.tasks.notifications import send_notification_stub

NotificationTask = Callable[[int, str], Awaitable[None]]


class MaintenanceRequestService:
    allowed_transitions = {
        RequestStatus.NEW: {RequestStatus.ASSIGNED, RequestStatus.CANCELLED},
        RequestStatus.ASSIGNED: {RequestStatus.IN_PROGRESS, RequestStatus.CANCELLED},
        RequestStatus.IN_PROGRESS: {RequestStatus.COMPLETED, RequestStatus.CANCELLED},
        RequestStatus.COMPLETED: set(),
        RequestStatus.CANCELLED: set(),
    }

    def __init__(
        self,
        session: AsyncSession,
        notification_task: NotificationTask = send_notification_stub,
    ) -> None:
        self.session = session
        self.repo = MaintenanceRequestRepository(session)
        self.equipment_repo = EquipmentRepository(session)
        self.employee_repo = EmployeeRepository(session)
        self.notification_task = notification_task

    async def list(
        self,
        skip: int,
        limit: int,
        status: RequestStatus | None,
        priority: RequestPriority | None,
        equipment_id: int | None,
        sort_desc: bool,
    ) -> list[MaintenanceRequest]:
        items = await self.repo.list_filtered(skip, limit, status, priority, equipment_id, sort_desc)
        for item in items:
            self._attach_resolution_seconds(item)
        return items

    async def get(self, item_id: int) -> MaintenanceRequest:
        item = await self.repo.get_with_relations(item_id)
        if not item:
            raise AppError(404, "Maintenance request not found", "REQUEST_NOT_FOUND")
        self._attach_resolution_seconds(item)
        return item

    async def create(self, data: MaintenanceRequestCreate) -> MaintenanceRequest:
        await self._ensure_refs(data.equipment_id, data.requester_id, data.assignee_id)
        if data.status == RequestStatus.COMPLETED:
            raise AppError(422, "Cannot create request directly as completed", "INVALID_STATUS_TRANSITION")
        item = await self.repo.create(data.model_dump())
        await self.session.commit()
        await self.notification_task(item.id, "created")
        return await self.get(item.id)

    async def update(self, item_id: int, data: MaintenanceRequestUpdate) -> MaintenanceRequest:
        item = await self.get(item_id)
        payload = data.model_dump(exclude_unset=True)
        await self._ensure_refs(
            payload.get("equipment_id", item.equipment_id),
            payload.get("requester_id", item.requester_id),
            payload.get("assignee_id", item.assignee_id),
        )
        new_status = payload.get("status")
        status_changed = new_status is not None and new_status != item.status
        if status_changed:
            self._validate_transition(item, new_status, payload)
            if new_status == RequestStatus.COMPLETED and "completed_at" not in payload:
                payload["completed_at"] = datetime.now(timezone.utc)
        if "completed_at" in payload and payload["completed_at"] and payload["completed_at"] < item.created_at:
            raise AppError(422, "completed_at must be greater than or equal to created_at", "INVALID_COMPLETED_AT")
        updated = await self.repo.update(item, payload)
        await self.session.commit()
        if status_changed:
            await self.notification_task(updated.id, f"status_changed:{updated.status}")
        return await self.get(updated.id)

    async def delete(self, item_id: int) -> None:
        await self.repo.delete(await self.get(item_id))
        await self.session.commit()

    async def _ensure_refs(self, equipment_id: int, requester_id: int, assignee_id: int | None) -> None:
        if not await self.equipment_repo.get(equipment_id):
            raise AppError(404, "Equipment not found", "EQUIPMENT_NOT_FOUND")
        if not await self.employee_repo.get(requester_id):
            raise AppError(404, "Requester not found", "REQUESTER_NOT_FOUND")
        if assignee_id and not await self.employee_repo.get(assignee_id):
            raise AppError(404, "Assignee not found", "ASSIGNEE_NOT_FOUND")

    def _validate_transition(
        self,
        item: MaintenanceRequest,
        new_status: RequestStatus,
        payload: dict[str, object],
    ) -> None:
        if new_status not in self.allowed_transitions[item.status]:
            raise AppError(422, f"Cannot transition from {item.status} to {new_status}", "INVALID_STATUS_TRANSITION")
        assignee_id = payload.get("assignee_id", item.assignee_id)
        forward_statuses = {RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED}
        if new_status in forward_statuses and not assignee_id:
            raise AppError(422, "Cannot move request forward without assignee", "ASSIGNEE_REQUIRED")

    def _attach_resolution_seconds(self, item: MaintenanceRequest) -> None:
        item.resolution_seconds = None
        if item.completed_at:
            item.resolution_seconds = int((item.completed_at - item.created_at).total_seconds())
