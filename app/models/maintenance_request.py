from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import RequestPriority, RequestStatus, RequestType
from app.models.mixins import TimestampMixin


class MaintenanceRequest(TimestampMixin, Base):
    __tablename__ = "maintenance_requests"
    __table_args__ = (
        Index("ix_requests_status_priority_equipment", "status", "priority", "equipment_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    type: Mapped[RequestType] = mapped_column(Enum(RequestType, name="request_type"), nullable=False)
    priority: Mapped[RequestPriority] = mapped_column(
        Enum(RequestPriority, name="request_priority"),
        nullable=False,
        index=True,
    )
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status"),
        default=RequestStatus.NEW,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    equipment = relationship("Equipment", back_populates="requests")
    requester = relationship("Employee", foreign_keys=[requester_id], back_populates="requested_requests")
    assignee = relationship("Employee", foreign_keys=[assignee_id], back_populates="assigned_requests")
    notifications = relationship("NotificationLog", back_populates="request", cascade="all, delete-orphan")
