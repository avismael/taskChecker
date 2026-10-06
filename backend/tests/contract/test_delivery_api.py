from datetime import date


def test_delivery_update_requires_authentication(client):
    response = client.patch("/deliveries/00000000-0000-0000-0000-000000000000", json={})
    assert response.status_code == 401


def test_authenticated_delivery_contract(client, unique_email):
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
    )
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "Delivery contract",
            "assigned_on": date(2026, 10, 1).isoformat(),
            "due_on": date(2026, 10, 10).isoformat(),
        },
    ).json()
    delivery = client.get(f"/tasks/{task['id']}/roster").json()[0]
    delivery_url = f"/deliveries/{delivery['id']}"

    status = client.patch(
        delivery_url,
        json={"status": "delivered", "actual_delivered_at": "2026-10-03T12:00:00Z"},
    )
    evidence = client.post(
        f"{delivery_url}/evidence/link", json={"url": "https://example.com/evidence"}
    )
    observation = client.post(
        f"{delivery_url}/observations", json={"body": "Private follow-up."}
    )
    history = client.get(f"{delivery_url}/history")

    assert status.status_code == 200
    assert status.json()["actual_delivered_at"] == "2026-10-03 12:00:00"
    without_date = client.patch(delivery_url, json={"status": "completed"})
    assert without_date.status_code == 200
    assert without_date.json()["actual_delivered_at"] is None
    assert evidence.status_code == 200
    assert observation.status_code == 200
    assert history.status_code == 200
    assert history.json()["events"]
