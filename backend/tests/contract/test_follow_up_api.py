from uuid import uuid4


def test_dashboard_requires_authentication(client):
    response = client.get("/dashboard")
    assert response.status_code == 401


def test_search_requires_authentication(client):
    response = client.get("/search", params={"q": "student"})
    assert response.status_code == 401


def test_profile_and_today_require_authentication(client):
    assert client.get(f"/students/{uuid4()}/profile").status_code == 401
    assert client.get("/today").status_code == 401


def test_authenticated_follow_up_contract(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200

    dashboard = client.get("/dashboard")
    today = client.get("/today")
    search = client.get("/search", params={"q": "student"})
    profile = client.get(f"/students/{uuid4()}/profile")

    assert dashboard.status_code == 200
    assert set(dashboard.json()) == {"active_tasks", "deliveries"}
    assert today.status_code == 200
    assert today.json()["dashboard"] == dashboard.json()
    assert search.status_code == 200
    assert search.json()["students"] == []
    assert profile.status_code == 422
