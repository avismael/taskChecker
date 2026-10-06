from datetime import date


def test_empty_and_archived_task_rosters_are_scoped(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "Empty"}).json()
    assert client.post(f"/subjects/{subject['id']}/sections/{section['id']}").status_code == 200
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "Empty roster",
            "assigned_on": date(2026, 10, 1).isoformat(),
            "due_on": date(2026, 10, 10).isoformat(),
        },
    ).json()

    assert client.get(f"/tasks/{task['id']}/roster").json() == []
    assert client.patch(f"/tasks/{task['id']}", json={"archived": True}).status_code == 200
    assert client.get("/tasks/data").json() == []


def test_task_roster_returns_student_display_fields(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    assert client.post(f"/subjects/{subject['id']}/sections/{section['id']}").status_code == 200
    client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "A-001",
            "first_name": "Ana",
            "last_name": "Lopez",
        },
    )
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "Roster display",
            "assigned_on": date(2026, 10, 1).isoformat(),
            "due_on": date(2026, 10, 10).isoformat(),
        },
    ).json()

    delivery = client.get(f"/tasks/{task['id']}/roster").json()[0]

    assert delivery["student_name"] == "Ana Lopez"
    assert delivery["student_nie"] == "A-001"
    assert delivery["student_id"]
