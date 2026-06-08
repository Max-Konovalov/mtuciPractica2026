from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_api_key
from app.dependencies.database import get_db_session
from app.models.enums import RequestPriority, RequestStatus
from app.schemas.maintenance_request import (
    MaintenanceRequestCreate,
    MaintenanceRequestRead,
    MaintenanceRequestUpdate,
)
from app.services.maintenance_request import MaintenanceRequestService

router = APIRouter(prefix="/requests", tags=["maintenance requests"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[MaintenanceRequestRead], summary="Список заявок на ТО")
async def list_requests(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[RequestStatus] = Query(default=None, alias="status"),
    priority: Optional[RequestPriority] = None,
    equipment_id: Optional[int] = Query(default=None, gt=0),
    sort_desc: bool = True,
) -> list[MaintenanceRequestRead]:
    return await MaintenanceRequestService(session).list(skip, limit, status_filter, priority, equipment_id, sort_desc)


@router.post("", response_model=MaintenanceRequestRead, status_code=status.HTTP_201_CREATED, summary="Создать заявку")
async def create_request(
    payload: MaintenanceRequestCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MaintenanceRequestRead:
    return await MaintenanceRequestService(session).create(payload)


@router.get("/{request_id}", response_model=MaintenanceRequestRead, summary="Получить заявку")
async def get_request(
    request_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MaintenanceRequestRead:
    return await MaintenanceRequestService(session).get(request_id)


@router.patch("/{request_id}", response_model=MaintenanceRequestRead, summary="Частично обновить заявку")
async def patch_request(
    request_id: int,
    payload: MaintenanceRequestUpdate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MaintenanceRequestRead:
    return await MaintenanceRequestService(session).update(request_id, payload)


@router.put("/{request_id}", response_model=MaintenanceRequestRead, summary="Полностью обновить заявку")
async def put_request(
    request_id: int,
    payload: MaintenanceRequestUpdate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MaintenanceRequestRead:
    return await MaintenanceRequestService(session).update(request_id, payload)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить заявку")
async def delete_request(request_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]) -> Response:
    await MaintenanceRequestService(session).delete(request_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
