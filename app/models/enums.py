from __future__ import annotations

from enum import Enum


class EquipmentStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class EmployeeRole(str, Enum):
    ENGINEER = "engineer"
    TECHNICIAN = "technician"
    MANAGER = "manager"


class RequestType(str, Enum):
    PLANNED = "плановое"
    UNSCHEDULED = "внеплановое"
    EMERGENCY = "аварийное"


class RequestPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RequestStatus(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    INTERNAL = "internal"


class NotificationStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"
    PENDING = "pending"
