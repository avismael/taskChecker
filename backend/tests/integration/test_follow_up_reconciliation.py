def test_report_requires_authentication(client):
    response = client.get("/reports/section")
    assert response.status_code == 401


def test_roster_profile_dashboard_and_search_reconcile(client, unique_email):
    client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    )
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Math"}).json()
    section = client.post("/sections", json={"name": "Second A"}).json()
    client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    student = client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "M-001",
            "first_name": "Maria",
            "last_name": "Perez",
        },
    ).json()
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "Reconcile",
            "assigned_on": "2026-10-01",
            "due_on": "2026-10-10",
        },
    ).json()
    roster = client.get(f"/tasks/{task['id']}/roster").json()
    delivery = next(row for row in roster if row["student_id"] == student["id"])
    client.patch(
        f"/deliveries/{delivery['id']}",
        json={"status": "completed", "actual_delivered_at": "2026-10-03T12:00:00Z"},
    )

    profile = client.get(f"/students/{student['id']}/profile").json()
    dashboard = client.get("/dashboard").json()
    search = client.get("/search", params={"q": "Maria"}).json()

    assert profile["task_count"] == len(roster) == 1
    assert profile["counts"]["completed"] == 1
    assert profile["compliance_percentage"] == 100.0
    assert dashboard["active_tasks"] == 1
    assert dashboard["deliveries"]["completed"] == 1
    assert search["students"] == [{"id": student["id"], "nie": "M-001", "name": "Maria Perez"}]
