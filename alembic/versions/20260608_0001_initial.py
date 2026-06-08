"""initial schema

Revision ID: 20260608_0001
Revises:
Create Date: 2026-06-08
"""

import sqlalchemy as sa

from alembic import op

revision = "20260608_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    equipment_status = sa.Enum("ACTIVE", "MAINTENANCE", "DECOMMISSIONED", name="equipment_status")
    employee_role = sa.Enum("ENGINEER", "TECHNICIAN", "MANAGER", name="employee_role")
    request_type = sa.Enum("PLANNED", "UNSCHEDULED", "EMERGENCY", name="request_type")
    request_priority = sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="request_priority")
    request_status = sa.Enum("NEW", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="request_status")
    notification_channel = sa.Enum("EMAIL", "INTERNAL", name="notification_channel")
    notification_status = sa.Enum("SENT", "FAILED", "PENDING", name="notification_status")

    bind = op.get_bind()
    for enum_type in (
        equipment_status,
        employee_role,
        request_type,
        request_priority,
        request_status,
        notification_channel,
        notification_status,
    ):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("serial_number", sa.String(length=128), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("status", equipment_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("serial_number"),
    )
    op.create_index("ix_equipment_name", "equipment", ["name"])
    op.create_index("ix_equipment_serial_number", "equipment", ["serial_number"])
    op.create_index("ix_equipment_status", "equipment", ["status"])

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", employee_role, nullable=False),
        sa.Column("contact_email", sa.String(length=320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contact_email"),
    )
    op.create_index("ix_employees_full_name", "employees", ["full_name"])

    op.create_table(
        "maintenance_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column("type", request_type, nullable=False),
        sa.Column("priority", request_priority, nullable=False),
        sa.Column("status", request_status, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["assignee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.ForeignKeyConstraint(["requester_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_maintenance_requests_equipment_id", "maintenance_requests", ["equipment_id"])
    op.create_index("ix_maintenance_requests_priority", "maintenance_requests", ["priority"])
    op.create_index("ix_maintenance_requests_status", "maintenance_requests", ["status"])
    op.create_index(
        "ix_requests_status_priority_equipment",
        "maintenance_requests",
        ["status", "priority", "equipment_id"],
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("status", notification_status, nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["request_id"], ["maintenance_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_logs_request_id", "notification_logs", ["request_id"])


def downgrade() -> None:
    op.drop_index("ix_notification_logs_request_id", table_name="notification_logs")
    op.drop_table("notification_logs")
    op.drop_index("ix_requests_status_priority_equipment", table_name="maintenance_requests")
    op.drop_index("ix_maintenance_requests_status", table_name="maintenance_requests")
    op.drop_index("ix_maintenance_requests_priority", table_name="maintenance_requests")
    op.drop_index("ix_maintenance_requests_equipment_id", table_name="maintenance_requests")
    op.drop_table("maintenance_requests")
    op.drop_index("ix_employees_full_name", table_name="employees")
    op.drop_table("employees")
    op.drop_index("ix_equipment_status", table_name="equipment")
    op.drop_index("ix_equipment_serial_number", table_name="equipment")
    op.drop_index("ix_equipment_name", table_name="equipment")
    op.drop_table("equipment")
    for enum_name in (
        "notification_status",
        "notification_channel",
        "request_status",
        "request_priority",
        "request_type",
        "employee_role",
        "equipment_status",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
