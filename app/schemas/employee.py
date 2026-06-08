from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import EmployeeRole


class EmployeeBase(BaseModel):
    full_name: str = Field(min_length=3, max_length=255, examples=["Иванов Иван Иванович"])
    role: EmployeeRole = Field(examples=[EmployeeRole.ENGINEER])
    contact_email: str = Field(max_length=320, examples=["ivanov@example.com"])

    @field_validator("contact_email")
    @classmethod
    def validate_email_shape(cls, value: str) -> str:
        if "@" not in value or "." not in value.rsplit("@", maxsplit=1)[-1]:
            raise ValueError("contact_email must be a valid email address")
        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=3, max_length=255)
    role: Optional[EmployeeRole] = None
    contact_email: Optional[str] = Field(default=None, max_length=320)

    @field_validator("contact_email")
    @classmethod
    def validate_email_shape(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and ("@" not in value or "." not in value.rsplit("@", maxsplit=1)[-1]):
            raise ValueError("contact_email must be a valid email address")
        return value


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
