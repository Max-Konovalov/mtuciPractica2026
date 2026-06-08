from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.enums import EquipmentStatus
from app.models.equipment import Equipment
from app.repositories.equipment import EquipmentRepository
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


class EquipmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = EquipmentRepository(session)

    async def list(self, skip: int, limit: int, status: EquipmentStatus | None, sort_desc: bool) -> list[Equipment]:
        return await self.repo.list_filtered(skip=skip, limit=limit, status=status, sort_desc=sort_desc)

    async def get(self, item_id: int) -> Equipment:
        item = await self.repo.get(item_id)
        if not item:
            raise AppError(404, "Equipment not found", "EQUIPMENT_NOT_FOUND")
        return item

    async def create(self, data: EquipmentCreate) -> Equipment:
        item = await self.repo.create(data.model_dump())
        await self.session.commit()
        return item

    async def update(self, item_id: int, data: EquipmentUpdate) -> Equipment:
        item = await self.get(item_id)
        updated = await self.repo.update(item, data.model_dump(exclude_unset=True))
        await self.session.commit()
        return updated

    async def delete(self, item_id: int) -> None:
        await self.repo.delete(await self.get(item_id))
        await self.session.commit()
