def test_report_requires_authentication(client):
    response = client.get("/reports/compliance")
    assert response.status_code == 401


def test_authenticated_report_format_contracts(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200

    print_report = client.get("/reports/section", params={"format": "print"})
    json_report = client.get("/reports/section", params={"format": "json"})
    unsupported = client.get("/reports/section", params={"format": "docx"})

    assert print_report.status_code == 200
    assert print_report.headers["content-type"].startswith("text/html")
    assert json_report.json() == {"type": "section", "rows": []}
    assert unsupported.status_code == 422
