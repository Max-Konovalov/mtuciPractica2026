from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EquipmentStatus


class EquipmentBase(BaseModel):
    name: str = Field(min_length=2, max_length=255, examples=["Компрессор Atlas Copco"])
    serial_number: str = Field(min_length=2, max_length=128, examples=["AC-2026-001"])
    location: str = Field(min_length=2, max_length=255, examples=["Цех 1"])
    status: EquipmentStatus = EquipmentStatus.ACTIVE


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    serial_number: Optional[str] = Field(default=None, min_length=2, max_length=128)
    location: Optional[str] = Field(default=None, min_length=2, max_length=255)
    status: Optional[EquipmentStatus] = None


class EquipmentRead(EquipmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
