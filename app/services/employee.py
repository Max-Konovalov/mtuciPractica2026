from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.employee import Employee
from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = EmployeeRepository(session)

    async def list(self, skip: int, limit: int, sort_desc: bool) -> list[Employee]:
        return await self.repo.list(skip=skip, limit=limit, sort_desc=sort_desc)

    async def get(self, item_id: int) -> Employee:
        item = await self.repo.get(item_id)
        if not item:
            raise AppError(404, "Employee not found", "EMPLOYEE_NOT_FOUND")
        return item

    async def create(self, data: EmployeeCreate) -> Employee:
        item = await self.repo.create(data.model_dump())
        await self.session.commit()
        return item

    async def update(self, item_id: int, data: EmployeeUpdate) -> Employee:
        item = await self.get(item_id)
        updated = await self.repo.update(item, data.model_dump(exclude_unset=True))
        await self.session.commit()
        return updated

    async def delete(self, item_id: int) -> None:
        await self.repo.delete(await self.get(item_id))
        await self.session.commit()
