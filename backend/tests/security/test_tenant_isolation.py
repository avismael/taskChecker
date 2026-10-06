from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.app.persistence.models.account import AccountRole, AccountStatus, TeacherAccount
from backend.app.persistence.session import SessionLocal
from backend.app.services.auth_service import hash_password
from backend.app.services.delivery_service import (
    add_file_evidence,
    add_link_evidence,
    add_observation,
    delivery_history,
)


def test_unauthenticated_pedagogical_access_is_denied(client):
    response = client.get("/admin/teachers")
    assert response.status_code in {401, 405}


@pytest.mark.parametrize(
    "path",
    [
        "/academic-years",
        "/organization/options",
        "/tasks/data",
        "/dashboard",
        "/today",
        "/search?q=student",
        "/reports/section",
        "/reports/pending",
        "/reports/compliance",
        f"/reports/individual/{uuid4()}",
        f"/tasks/{uuid4()}/roster",
        f"/deliveries/{uuid4()}/history",
    ],
)
def test_unauthenticated_data_endpoints_are_denied(client, path):
    response = client.get(path)
    assert response.status_code == 401, path


def test_administrator_cannot_access_pedagogical_endpoints(client):
    admin_email = f"admin-{uuid4().hex}@example.com"
    with SessionLocal() as session:
        session.add(
            TeacherAccount(
                email=admin_email,
                password_hash=hash_password("admin-password"),
                role=AccountRole.ADMINISTRATOR,
                status=AccountStatus.ACTIVE,
                tenant_id=None,
            )
        )
        session.commit()

    assert client.post(
        "/auth/login", json={"email": admin_email, "password": "admin-password"}
    ).status_code == 200
    for path in ("/tasks/data", "/dashboard", "/reports/compliance"):
        assert client.get(path).status_code == 403, path


@pytest.mark.parametrize(
    "operation",
    [
        lambda session, tenant, delivery: add_observation(session, tenant, delivery, uuid4(), "private"),
        lambda session, tenant, delivery: add_link_evidence(session, tenant, delivery, uuid4(), "https://example.com"),
        lambda session, tenant, delivery: add_file_evidence(session, tenant, delivery, uuid4(), "file.pdf", "application/pdf", b"pdf"),
        lambda session, tenant, delivery: delivery_history(session, tenant, delivery),
    ],
)
def test_delivery_mutations_reject_foreign_delivery(operation):
    session = Mock()
    session.scalar.return_value = None
    with pytest.raises(ValueError, match="Delivery not found"):
        operation(session, uuid4(), uuid4())


def test_authenticated_teacher_cannot_read_foreign_pedagogical_records(client):
    teacher_a = f"teacher-a-{uuid4().hex}@example.com"
    teacher_b = f"teacher-b-{uuid4().hex}@example.com"
    assert client.post("/auth/register", json={"email": teacher_a, "password": "safe-password"}).status_code == 201
    assert client.post("/auth/login", json={"email": teacher_a, "password": "safe-password"}).status_code == 200

    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Math"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    assert client.post(f"/subjects/{subject['id']}/sections/{section['id']}").status_code == 200
    student = client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": f"A-{uuid4().hex[:8]}",
            "first_name": "Private",
            "last_name": "Student",
        },
    ).json()
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "Private task",
            "assigned_on": date(2026, 10, 1).isoformat(),
            "due_on": date(2026, 10, 10).isoformat(),
        },
    ).json()
    delivery = client.get(f"/tasks/{task['id']}/roster").json()[0]

    assert client.post("/auth/register", json={"email": teacher_b, "password": "safe-password"}).status_code == 201
    assert client.post("/auth/login", json={"email": teacher_b, "password": "safe-password"}).status_code == 200

    assert client.get("/tasks/data").json() == []
    assert client.get(f"/tasks/{task['id']}/roster").status_code == 422
    assert client.get(f"/students/{student['id']}/profile").status_code == 422
    assert client.get(f"/deliveries/{delivery['id']}/history").status_code == 422
    assert client.patch(f"/tasks/{task['id']}", json={"title": "Tampered"}).status_code == 422
    assert client.patch(f"/deliveries/{delivery['id']}", json={"status": "completed"}).status_code == 422
    assert client.post(
        f"/deliveries/{delivery['id']}/observations",
        json={"body": "Foreign note"},
    ).status_code == 422
    assert client.post(
        f"/deliveries/{delivery['id']}/evidence/link",
        json={"url": "https://example.com/foreign"},
    ).status_code == 422
    assert client.get(f"/reports/individual/{student['id']}").json() == {
        "type": "individual",
        "rows": [],
    }


def test_two_teachers_and_administrator_cannot_cross_pedagogical_boundary(client):
    teacher_a = f"boundary-a-{uuid4().hex}@example.com"
    teacher_b = f"boundary-b-{uuid4().hex}@example.com"
    admin_email = f"boundary-admin-{uuid4().hex}@example.com"
    assert client.post(
        "/auth/register", json={"email": teacher_a, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": teacher_a, "password": "safe-password"}
    ).status_code == 200
    year = client.post("/academic-years", json={"name": "2028"}).json()
    subject = client.post("/subjects", json={"name": "Boundary"}).json()
    section = client.post("/sections", json={"name": "Boundary A"}).json()
    client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    student = client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "BOUNDARY-001",
            "first_name": "Boundary",
            "last_name": "Student",
        },
    ).json()
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "Boundary task",
            "assigned_on": "2028-01-01",
            "due_on": "2028-01-10",
        },
    ).json()

    assert client.post(
        "/auth/register", json={"email": teacher_b, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": teacher_b, "password": "safe-password"}
    ).status_code == 200
    assert client.get(f"/students/{student['id']}/profile").status_code == 422
    assert client.get(f"/tasks/{task['id']}/roster").status_code == 422
    assert client.get("/tasks/data").json() == []

    with SessionLocal() as session:
        session.add(
            TeacherAccount(
                email=admin_email,
                password_hash=hash_password("admin-password"),
                role=AccountRole.ADMINISTRATOR,
                status=AccountStatus.ACTIVE,
                tenant_id=None,
            )
        )
        session.commit()
    assert client.post(
        "/auth/login", json={"email": admin_email, "password": "admin-password"}
    ).status_code == 200
    assert client.get("/tasks/data").status_code == 403
    assert client.get("/dashboard").status_code == 403
    assert client.get(f"/students/{student['id']}/profile").status_code == 403
