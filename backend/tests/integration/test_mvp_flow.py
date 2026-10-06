from datetime import date
from uuid import UUID

from sqlalchemy import select

from backend.app.persistence.models.audit import AuditEvent
from backend.app.persistence.session import SessionLocal


def test_authenticated_setup_task_and_delivery_flow(client, unique_email):
    registered = client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    )
    assert registered.status_code == 201
    login = client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    )
    assert login.status_code == 200
    tenant_id = UUID(login.json()["tenant_id"])

    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    assert client.post(f"/subjects/{subject['id']}/sections/{section['id']}").status_code == 200
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
        files={"file": ("students.csv", "nie,nombre,apellido\nB2,Second,Student\n", "text/csv")},
    )
    assert imported.json() == {"imported": 1}
    task = client.post(
        "/tasks",
        json={
            "academic_year_id": year["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "title": "First activity",
            "description": "Deliver the activity",
            "assigned_on": date(2026, 10, 1).isoformat(),
            "due_on": date(2026, 10, 10).isoformat(),
        },
    ).json()
    roster = client.get(f"/tasks/{task['id']}/roster").json()
    assert len(roster) == 2
    assert roster[0]["actual_delivered_at"] is None
    assert roster[0]["evidence_count"] == 0
    assert roster[0]["observation_count"] == 0
    first_delivery = next(row for row in roster if row["student_id"] == student["id"])
    assert client.patch(
        f"/deliveries/{first_delivery['id']}",
        json={"status": "delivered", "actual_delivered_at": "2026-10-03T12:00:00Z"},
    ).status_code == 200
    uploaded = client.post(
        f"/deliveries/{first_delivery['id']}/evidence",
        files={"file": ("evidence.pdf", b"%PDF-test", "application/pdf")},
    )
    assert uploaded.status_code == 200
    observed = client.post(
        f"/deliveries/{first_delivery['id']}/observations",
        json={"body": "Needs a quieter follow-up."},
    )
    assert observed.status_code == 200
    second_observed = client.post(
        f"/deliveries/{first_delivery['id']}/observations",
        json={"body": "Follow-up scheduled."},
    )
    linked = client.post(
        f"/deliveries/{first_delivery['id']}/evidence/link",
        json={"url": "https://example.com/evidence"},
    )
    assert second_observed.status_code == 200
    assert linked.status_code == 200
    updated_roster = client.get(f"/tasks/{task['id']}/roster").json()
    updated_first = next(row for row in updated_roster if row["id"] == first_delivery["id"])
    assert updated_first["actual_delivered_at"] is not None
    assert updated_first["evidence_count"] == 2
    assert updated_first["observation_count"] == 2
    assert updated_first["observation_summary"] == "Follow-up scheduled."
    profile = client.get(f"/students/{student['id']}/profile")
    dashboard = client.get("/dashboard")
    today = client.get("/today")
    search = client.get("/search", params={"q": "Ana"})
    assert profile.json()["task_count"] == 1
    assert profile.json()["counts"]["delivered"] == 1
    assert dashboard.json()["deliveries"]["delivered"] == 1
    assert today.json()["dashboard"] == dashboard.json()
    assert search.json()["students"][0]["id"] == student["id"]
    completed = client.patch(
        f"/deliveries/{first_delivery['id']}",
        json={"status": "completed", "actual_delivered_at": "2026-10-03T12:00:00Z"},
    )
    completed_profile = client.get(f"/students/{student['id']}/profile")
    assert completed.status_code == 200
    assert completed_profile.json()["counts"]["completed"] == 1
    assert completed_profile.json()["compliance_percentage"] == 100.0
    rejected = client.post(
        f"/deliveries/{first_delivery['id']}/evidence",
        files={"file": ("evidence.zip", b"PK", "application/zip")},
    )
    assert rejected.status_code == 422
    history = client.get(f"/deliveries/{first_delivery['id']}/history")
    assert history.status_code == 200
    assert any(event["resource_type"] == "evidence" for event in history.json()["events"])
    section_pdf = client.get("/reports/section", params={"format": "pdf"})
    pending_xlsx = client.get("/reports/pending", params={"format": "xlsx"})
    compliance_csv = client.get("/reports/compliance", params={"format": "csv"})
    individual_json = client.get(
        f"/reports/individual/{student['id']}", params={"format": "json"}
    )
    individual_print = client.get(
        f"/reports/individual/{student['id']}", params={"format": "print"}
    )
    unsupported = client.get("/reports/section", params={"format": "docx"})
    assert section_pdf.headers["content-type"] == "application/pdf"
    assert pending_xlsx.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert compliance_csv.headers["content-type"].startswith("text/csv")
    assert individual_json.json()["rows"][0]["student"] == "Ana Lopez"
    assert individual_print.headers["content-type"].startswith("text/html")
    assert unsupported.status_code == 422
    with SessionLocal() as session:
        events = list(
            session.scalars(
                select(AuditEvent).where(AuditEvent.tenant_id == tenant_id)
            ).all()
        )
    assert {"created", "committed", "status_changed"}.issubset({event.action for event in events})
    assert all(event.actor_account_id is not None for event in events if event.automation_source is None)
