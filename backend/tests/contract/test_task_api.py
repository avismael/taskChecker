from datetime import date
from uuid import uuid4


def test_task_creation_requires_authentication(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 401


def test_teacher_can_list_update_and_archive_tasks(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    payload = {
        "academic_year_id": year["id"],
        "subject_id": subject["id"],
        "section_id": section["id"],
        "title": "First activity",
        "description": "Initial description",
        "assigned_on": date(2026, 10, 1).isoformat(),
        "due_on": date(2026, 10, 10).isoformat(),
    }
    task = client.post("/tasks", json=payload).json()
    assert client.get("/tasks/data").json() == [
        {"id": task["id"], "title": "First activity", "due_on": "2026-10-10"}
    ]

    updated = client.patch(
        f"/tasks/{task['id']}",
        json={"title": "Updated activity", "due_on": "2026-10-12"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated activity"
    archived = client.patch(f"/tasks/{task['id']}", json={"archived": True})
    assert archived.status_code == 200
    assert archived.json()["archived"] is True
    assert client.get("/tasks/data").json() == []


def test_authenticated_task_payload_validates_required_fields_and_dates(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200

    missing_fields = client.post("/tasks", json={})
    invalid_dates = client.post(
        "/tasks",
        json={
            "academic_year_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "section_id": str(uuid4()),
            "title": "Invalid task",
            "assigned_on": "2026-10-10",
            "due_on": "2026-10-01",
        },
    )

    assert missing_fields.status_code == 422
    assert invalid_dates.status_code == 422


def test_task_creation_reports_missing_subject_section_link(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()

    response = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "First activity",
            "assigned_on": "2026-10-01",
            "due_on": "2026-10-10",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "La asignatura no está vinculada a la sección seleccionada.",
        "fields": {},
    }
