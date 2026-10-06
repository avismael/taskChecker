import pytest
from sqlalchemy.orm import Session

from backend.app.persistence.models.audit import AuditEvent
from backend.app.persistence.models.delivery import Delivery, DeliveryStatus
from backend.app.persistence.session import SessionLocal


def test_delivery_update_requires_authenticated_teacher(client):
    response = client.patch("/deliveries/00000000-0000-0000-0000-000000000000", json={})
    assert response.status_code == 401


def test_delivery_mutation_failure_rolls_back_status_and_audit(client, unique_email, monkeypatch):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Science"}).json()
    section = client.post("/sections", json={"name": "Third A"}).json()
    client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "D-001",
            "first_name": "Dana",
            "last_name": "Test",
        },
    )
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "Rollback",
            "assigned_on": "2026-10-01",
            "due_on": "2026-10-10",
        },
    ).json()
    delivery = client.get(f"/tasks/{task['id']}/roster").json()[0]

    original_commit = Session.commit

    def fail_commit(session):
        raise RuntimeError("forced commit failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    with pytest.raises(RuntimeError, match="forced commit failure"):
        client.patch(
            f"/deliveries/{delivery['id']}",
            json={"status": "delivered", "actual_delivered_at": "2026-10-03T12:00:00Z"},
        )
    monkeypatch.setattr(Session, "commit", original_commit)

    with SessionLocal() as session:
        delivery_id = __import__("uuid").UUID(delivery["id"])
        persisted = session.get(Delivery, delivery_id)
        events = session.query(AuditEvent).filter(AuditEvent.resource_id == str(delivery_id)).all()
        assert persisted.status == DeliveryStatus.PENDING
        assert events == []
