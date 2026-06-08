from __future__ import annotations

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import selectinload

from app.models.enums import RequestPriority, RequestStatus
from app.models.maintenance_request import MaintenanceRequest
from app.repositories.base import BaseRepository


class MaintenanceRequestRepository(BaseRepository[MaintenanceRequest]):
    model = MaintenanceRequest

    async def get_with_relations(self, item_id: int) -> MaintenanceRequest | None:
        query = (
            select(MaintenanceRequest)
            .options(
                selectinload(MaintenanceRequest.equipment),
                selectinload(MaintenanceRequest.requester),
                selectinload(MaintenanceRequest.assignee),
            )
            .where(MaintenanceRequest.id == item_id)
        )
        return (await self.session.scalars(query)).first()

    async def list_filtered(
        self,
        skip: int = 0,
        limit: int = 50,
        status: RequestStatus | None = None,
        priority: RequestPriority | None = None,
        equipment_id: int | None = None,
        sort_desc: bool = True,
    ) -> list[MaintenanceRequest]:
        query = select(MaintenanceRequest).options(
            selectinload(MaintenanceRequest.equipment),
            selectinload(MaintenanceRequest.requester),
            selectinload(MaintenanceRequest.assignee),
        )
        if status:
            query = query.where(MaintenanceRequest.status == status)
        if priority:
            query = query.where(MaintenanceRequest.priority == priority)
        if equipment_id:
            query = query.where(MaintenanceRequest.equipment_id == equipment_id)
        query = query.order_by(desc(MaintenanceRequest.created_at) if sort_desc else asc(MaintenanceRequest.created_at))
        return await self.scalars(query.offset(skip).limit(limit))
