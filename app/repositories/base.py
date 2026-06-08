from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import Select, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, item_id: int) -> ModelT | None:
        return await self.session.get(self.model, item_id)

    async def list(self, skip: int = 0, limit: int = 50, sort_desc: bool = True) -> list[ModelT]:
        query = select(self.model).offset(skip).limit(limit)
        if hasattr(self.model, "created_at"):
            order = desc(self.model.created_at) if sort_desc else asc(self.model.created_at)
            query = query.order_by(order)
        return list((await self.session.scalars(query)).all())

    async def create(self, data: dict[str, Any]) -> ModelT:
        item = self.model(**data)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update(self, item: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(item, key, value)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete(self, item: ModelT) -> None:
        await self.session.delete(item)
        await self.session.flush()

    async def scalars(self, query: Select[tuple[ModelT]]) -> list[ModelT]:
        return list((await self.session.scalars(query)).all())
