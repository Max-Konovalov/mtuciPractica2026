from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_api_key
from app.dependencies.database import get_db_session
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.employee import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[EmployeeRead], summary="Список сотрудников")
async def list_employees(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_desc: bool = True,
) -> list[EmployeeRead]:
    return await EmployeeService(session).list(skip, limit, sort_desc)


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED, summary="Создать сотрудника")
async def create_employee(
    payload: EmployeeCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EmployeeRead:
    return await EmployeeService(session).create(payload)


@router.get("/{employee_id}", response_model=EmployeeRead, summary="Получить сотрудника")
async def get_employee(employee_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]) -> EmployeeRead:
    return await EmployeeService(session).get(employee_id)


@router.put("/{employee_id}", response_model=EmployeeRead, summary="Обновить сотрудника")
async def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EmployeeRead:
    return await EmployeeService(session).update(employee_id, payload)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить сотрудника")
async def delete_employee(employee_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]) -> Response:
    await EmployeeService(session).delete(employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
