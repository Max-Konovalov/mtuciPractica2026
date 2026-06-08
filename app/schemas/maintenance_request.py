from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import RequestPriority, RequestStatus, RequestType
from app.schemas.employee import EmployeeRead
from app.schemas.equipment import EquipmentRead


class MaintenanceRequestBase(BaseModel):
    equipment_id: int = Field(gt=0, examples=[1])
    requester_id: int = Field(gt=0, examples=[1])
    assignee_id: Optional[int] = Field(default=None, gt=0, examples=[2])
    type: RequestType = Field(examples=[RequestType.PLANNED])
    priority: RequestPriority = Field(examples=[RequestPriority.MEDIUM])
    status: RequestStatus = RequestStatus.NEW
    description: str = Field(min_length=5, examples=["Плановая замена фильтра и диагностика"])
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class MaintenanceRequestCreate(MaintenanceRequestBase):
    @model_validator(mode="after")
    def validate_create_state(self) -> "MaintenanceRequestCreate":
        if self.status == RequestStatus.COMPLETED and self.assignee_id is None:
            raise ValueError("Нельзя закрыть заявку без назначенного исполнителя")
        if self.status in {RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS} and self.assignee_id is None:
            raise ValueError("Нельзя продвинуть заявку без назначенного исполнителя")
        return self


class MaintenanceRequestUpdate(BaseModel):
    equipment_id: Optional[int] = Field(default=None, gt=0)
    requester_id: Optional[int] = Field(default=None, gt=0)
    assignee_id: Optional[int] = Field(default=None, gt=0)
    type: Optional[RequestType] = None
    priority: Optional[RequestPriority] = None
    status: Optional[RequestStatus] = None
    description: Optional[str] = Field(default=None, min_length=5)
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class MaintenanceRequestRead(MaintenanceRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    resolution_seconds: Optional[int] = None
    equipment: Optional[EquipmentRead] = None
    requester: Optional[EmployeeRead] = None
    assignee: Optional[EmployeeRead] = None

    @model_validator(mode="after")
    def validate_completed_at(self) -> "MaintenanceRequestRead":
        if self.completed_at and self.completed_at < self.created_at:
            raise ValueError("completed_at must be greater than or equal to created_at")
        return self
