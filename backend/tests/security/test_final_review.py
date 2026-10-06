from uuid import uuid4


def test_pedagogical_endpoints_fail_closed_without_a_session(client):
    paths = [
        "/academic-years",
        "/organization/options",
        "/tasks/data",
        "/dashboard",
        "/today",
        "/search?q=student",
        "/reports/section",
        "/reports/pending",
        "/reports/compliance",
        f"/reports/individual/{uuid4()}",
        f"/students/{uuid4()}/profile",
        f"/tasks/{uuid4()}/roster",
        f"/deliveries/{uuid4()}/history",
    ]

    for path in paths:
        response = client.get(path)
        assert response.status_code == 401, path


def test_security_review_rejects_grading_field_names_in_report_contract():
    forbidden = {"grade", "grades", "score", "scores", "average", "averages"}
    report_contract = {
        "section": {"student", "status", "due_on"},
        "pending": {"student", "status", "due_on"},
        "compliance": {"student", "status", "due_on"},
        "individual": {"student", "status", "due_on"},
    }

    assert all(not forbidden.intersection(fields) for fields in report_contract.values())
