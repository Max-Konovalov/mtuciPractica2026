from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_api_key
from app.dependencies.database import get_db_session
from app.models.enums import EquipmentStatus
from app.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate
from app.services.equipment import EquipmentService

router = APIRouter(prefix="/equipment", tags=["equipment"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[EquipmentRead], summary="Список оборудования")
async def list_equipment(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[EquipmentStatus] = Query(default=None, alias="status"),
    sort_desc: bool = True,
) -> list[EquipmentRead]:
    return await EquipmentService(session).list(skip, limit, status_filter, sort_desc)


@router.post("", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED, summary="Создать оборудование")
async def create_equipment(
    payload: EquipmentCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EquipmentRead:
    return await EquipmentService(session).create(payload)


@router.get("/{equipment_id}", response_model=EquipmentRead, summary="Получить оборудование")
async def get_equipment(equipment_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]) -> EquipmentRead:
    return await EquipmentService(session).get(equipment_id)


@router.put("/{equipment_id}", response_model=EquipmentRead, summary="Обновить оборудование")
async def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EquipmentRead:
    return await EquipmentService(session).update(equipment_id, payload)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить оборудование")
async def delete_equipment(equipment_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]) -> Response:
    await EquipmentService(session).delete(equipment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
