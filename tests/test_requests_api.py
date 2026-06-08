from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_request_and_validate_status_transition(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    equipment = (
        await client.post(
            "/equipment",
            headers=auth_headers,
            json={"name": "Насос", "serial_number": "P-100", "location": "Цех 2", "status": "active"},
        )
    ).json()
    requester = (
        await client.post(
            "/employees",
            headers=auth_headers,
            json={"full_name": "Петров Петр", "role": "engineer", "contact_email": "petrov@example.com"},
        )
    ).json()
    assignee = (
        await client.post(
            "/employees",
            headers=auth_headers,
            json={"full_name": "Сидоров Семен", "role": "technician", "contact_email": "sidorov@example.com"},
        )
    ).json()

    response = await client.post(
        "/requests",
        headers=auth_headers,
        json={
            "equipment_id": equipment["id"],
            "requester_id": requester["id"],
            "assignee_id": assignee["id"],
            "type": "плановое",
            "priority": "high",
            "status": "new",
            "description": "Проверка давления",
        },
    )
    assert response.status_code == 201
    request_id = response.json()["id"]

    bad_transition = await client.patch(
        f"/requests/{request_id}",
        headers=auth_headers,
        json={"status": "completed"},
    )
    assert bad_transition.status_code == 422
    assert bad_transition.json()["code"] == "INVALID_STATUS_TRANSITION"

    assigned = await client.patch(f"/requests/{request_id}", headers=auth_headers, json={"status": "assigned"})
    assert assigned.status_code == 200
    assert assigned.json()["status"] == "assigned"
