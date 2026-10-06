from datetime import date


def test_delivery_state_matrix_and_manual_correction(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "A-001",
            "first_name": "Ana",
            "last_name": "Lopez",
        },
    ).json()
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "State matrix",
            "assigned_on": date(2026, 10, 1).isoformat(),
            "due_on": date(2026, 10, 10).isoformat(),
        },
    ).json()
    delivery = client.get(f"/tasks/{task['id']}/roster").json()[0]
    delivery_url = f"/deliveries/{delivery['id']}"

    for status in ("pending", "delivered", "not_delivered", "late", "completed"):
        payload = {"status": status}
        if status in {"delivered", "late", "completed"}:
            payload["actual_delivered_at"] = "2026-10-03T12:00:00Z"
        response = client.patch(delivery_url, json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == status

    corrected = client.patch(
        delivery_url,
        json={"status": "not_delivered", "actual_delivered_at": None},
    )
    assert corrected.status_code == 200
    assert corrected.json()["status"] == "not_delivered"
    assert corrected.json()["actual_delivered_at"] is None
