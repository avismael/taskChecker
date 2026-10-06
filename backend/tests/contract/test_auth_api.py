from uuid import uuid4

from backend.app.persistence.models.account import AccountRole, AccountStatus, TeacherAccount
from backend.app.persistence.session import SessionLocal
from backend.app.services.auth_service import hash_password


def test_health_endpoint_is_available(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_teacher_registration_returns_private_account(client, unique_email):
    response = client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == unique_email


def test_authentication_recovery_and_password_change(client, unique_email):
    password = "safe-password"
    assert client.post("/auth/register", json={"email": unique_email, "password": password}).status_code == 201
    login = client.post("/auth/login", json={"email": unique_email, "password": password})
    assert login.status_code == 200
    recovery = client.post("/auth/recovery", json={"email": unique_email})
    assert recovery.status_code == 200
    assert recovery.json()["accepted"] is True
    changed = client.post("/auth/password", json={"email": unique_email, "password": "new-password"})
    assert changed.status_code == 200


def test_logout_clears_authenticated_session(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    page = client.get("/workspace")
    csrf_token = page.text.split('name="csrf-token" content="', 1)[1].split('"', 1)[0]

    response = client.post(
        "/auth/logout",
        headers={"sec-fetch-site": "same-origin", "X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 200
    assert response.json() == {"logged_out": True}
    assert client.get("/workspace", follow_redirects=False).headers["location"] == "/login"


def test_logout_is_safe_without_authenticated_session(client):
    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"logged_out": True}


def test_browser_logout_requires_csrf_token(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})

    response = client.post("/auth/logout", headers={"sec-fetch-site": "same-origin"})

    assert response.status_code == 403
    assert client.get("/workspace").status_code == 200


def test_administrator_can_suspend_and_reactivate_teacher(client, unique_email):
    teacher = client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).json()
    admin_email = f"admin-{uuid4().hex}@example.com"
    with SessionLocal() as session:
        session.add(
            TeacherAccount(
                email=admin_email,
                password_hash=hash_password("admin-password"),
                role=AccountRole.ADMINISTRATOR,
                status=AccountStatus.ACTIVE,
                tenant_id=None,
            )
        )
        session.commit()

    assert client.post(
        "/auth/login", json={"email": admin_email, "password": "admin-password"}
    ).status_code == 200
    suspended = client.patch(
        f"/admin/teachers/{teacher['id']}", json={"status": "suspended"}
    )
    assert suspended.status_code == 200
    assert suspended.json()["status"] == "suspended"

    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 401
    assert client.post(
        "/auth/login", json={"email": admin_email, "password": "admin-password"}
    ).status_code == 200
    reactivated = client.patch(
        f"/admin/teachers/{teacher['id']}", json={"status": "active"}
    )
    assert reactivated.status_code == 200
    assert reactivated.json()["status"] == "active"
