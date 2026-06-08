from __future__ import annotations

from sqlalchemy import asc, desc, select

from app.models.enums import EquipmentStatus
from app.models.equipment import Equipment
from app.repositories.base import BaseRepository


class EquipmentRepository(BaseRepository[Equipment]):
    model = Equipment

    async def list_filtered(
        self,
        skip: int = 0,
        limit: int = 50,
        status: EquipmentStatus | None = None,
        sort_desc: bool = True,
    ) -> list[Equipment]:
        query = select(Equipment)
        if status:
            query = query.where(Equipment.status == status)
        query = query.order_by(desc(Equipment.created_at) if sort_desc else asc(Equipment.created_at))
        return await self.scalars(query.offset(skip).limit(limit))
