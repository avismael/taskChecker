from sqlalchemy import select

from backend.app.persistence.models.audit import AuditEvent
from backend.app.persistence.session import SessionLocal


def test_registration_creates_audit_event(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    with SessionLocal() as session:
        event = session.scalar(select(AuditEvent).where(AuditEvent.action == "registered"))
    assert event is not None
