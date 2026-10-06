from uuid import UUID

from sqlalchemy import func, select

from backend.app.persistence.models.organization import Student
from backend.app.persistence.session import SessionLocal


def test_organization_endpoints_require_authentication(client):
    response = client.post("/academic-years", json={"name": "2026"})
    assert response.status_code == 401


def test_academic_year_can_be_closed_and_listed(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    assert client.post("/auth/login", json={"email": unique_email, "password": "safe-password"}).status_code == 200
    year = client.post("/academic-years", json={"name": "2026"}).json()
    closed = client.post(f"/academic-years/{year['id']}/close")
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"
    listed = client.get("/academic-years")
    assert listed.json() == [{"id": year["id"], "label": "2026", "status": "closed"}]
    next_year = client.post("/academic-years", json={"name": "2027"})
    assert next_year.status_code == 200
    assert {item["status"] for item in client.get("/academic-years").json()} == {"active", "closed"}


def test_mixed_validity_import_previews_errors_and_blocks_commit(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    login = client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    )
    assert login.status_code == 200
    tenant_id = UUID(login.json()["tenant_id"])
    year = client.post("/academic-years", json={"name": "2027"}).json()
    section = client.post("/sections", json={"name": "Import A"}).json()
    content = "nie,nombre,apellido\nA-001,Ana,Lopez\n,Ana,Missing\nA-001,Ana,Duplicate\n"

    preview = client.post(
        "/students/imports/preview",
        files={"file": ("students.csv", content, "text/csv")},
    )
    assert preview.status_code == 200
    assert preview.json()["critical_errors"] == 2
    assert preview.json()["rows"][1]["errors"] == ["NIE is required"]
    assert preview.json()["rows"][2]["errors"] == ["Duplicate NIE in import"]

    blocked = client.post(
        "/students/imports/commit",
        params={"academic_year_id": year["id"], "section_id": section["id"]},
        files={"file": ("students.csv", content, "text/csv")},
    )
    assert blocked.status_code == 422

    with SessionLocal() as session:
        count = session.scalar(select(func.count(Student.id)).where(Student.tenant_id == tenant_id))
    assert count == 0
