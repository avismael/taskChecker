from uuid import UUID

from sqlalchemy import select

from backend.app.persistence.models.audit import AuditEvent
from backend.app.persistence.session import SessionLocal


def test_organization_mutations_are_audited(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    login = client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    )
    tenant_id = UUID(login.json()["tenant_id"])
    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    second_section = client.post("/sections", json={"name": "First B"}).json()
    client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    student = client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "A-001",
            "first_name": "Ana",
            "last_name": "Lopez",
        },
    ).json()
    imported = client.post(
        "/students/imports/commit",
        params={"academic_year_id": year["id"], "section_id": section["id"]},
        files={"file": ("students.csv", "nie,nombre,apellido\nB-002,Bob,Smith\n", "text/csv")},
    )
    assert imported.json() == {"imported": 1}
    assert client.patch(
        f"/students/{student['id']}/membership",
        json={"academic_year_id": year["id"], "section_id": second_section["id"]},
    ).status_code == 200
    assert client.patch(f"/subjects/{subject['id']}", json={"archived": True}).status_code == 200
    assert client.patch(f"/sections/{section['id']}", json={"archived": True}).status_code == 200
    assert client.post(f"/academic-years/{year['id']}/close").status_code == 200

    with SessionLocal() as session:
        events = session.scalars(
            select(AuditEvent).where(AuditEvent.tenant_id == tenant_id)
        ).all()

    audited = {(event.resource_type, event.action) for event in events}
    assert ("student_import", "committed") in audited
    assert ("student_membership", "transferred") in audited
    assert ("subject", "archived") in audited
    assert ("section", "archived") in audited
    assert ("academic_year", "closed") in audited
