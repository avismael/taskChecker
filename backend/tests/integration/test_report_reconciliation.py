def test_all_report_types_reconcile_without_grading_fields(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200
    year = client.post("/academic-years", json={"name": "2026"}).json()
    section = client.post("/sections", json={"name": "Report A"}).json()
    student = client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "R-001",
            "first_name": "Report",
            "last_name": "Student",
        },
    ).json()

    reports = [
        client.get("/reports/section", params={"format": "json"}),
        client.get("/reports/pending", params={"format": "json"}),
        client.get("/reports/compliance", params={"format": "json"}),
        client.get(f"/reports/individual/{student['id']}", params={"format": "json"}),
    ]

    assert all(report.status_code == 200 for report in reports)
    payloads = [report.json() for report in reports]
    assert payloads[0]["rows"] == []
    assert payloads[1]["rows"] == []
    assert payloads[2]["rows"] == []
    assert payloads[3]["rows"] == []
    assert all(
        not any(key in row for key in ("grade", "score", "average"))
        for payload in payloads
        for row in payload["rows"]
    )
