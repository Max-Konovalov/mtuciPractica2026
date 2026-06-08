from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EmployeeRole


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[EmployeeRole] = mapped_column(Enum(EmployeeRole, name="employee_role"), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    requested_requests = relationship(
        "MaintenanceRequest",
        foreign_keys="MaintenanceRequest.requester_id",
        back_populates="requester",
    )
    assigned_requests = relationship(
        "MaintenanceRequest",
        foreign_keys="MaintenanceRequest.assignee_id",
        back_populates="assignee",
    )
