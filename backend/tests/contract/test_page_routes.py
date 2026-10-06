def test_public_home_redirects_to_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_requests_return_correlation_id(client):
    response = client.get("/health", headers={"X-Request-ID": "request-test-1"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "request-test-1"


def test_authenticated_page_contains_csrf_token(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/workspace")
    assert response.status_code == 200
    assert 'name="csrf-token"' in response.text


def test_authenticated_page_shows_user_control(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})

    response = client.get("/workspace")

    assert response.status_code == 200
    assert unique_email in response.text
    assert 'id="logout-button"' in response.text
    assert 'aria-label="Menú de usuario"' in response.text


def test_workspace_exposes_live_metric_targets(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/workspace")
    assert response.status_code == 200
    assert 'id="workspace-active-tasks"' in response.text
    assert 'id="workspace-pending-deliveries"' in response.text
    assert 'id="workspace-follow-up"' in response.text


def test_browser_mutation_requires_csrf_token(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    blocked = client.post(
        "/academic-years",
        json={"name": "2026-2027"},
        headers={"sec-fetch-site": "same-origin"},
    )
    assert blocked.status_code == 403


def test_login_page_has_labeled_form(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert 'id="email"' in response.text
    assert 'id="password"' in response.text


def test_auth_pages_are_available(client):
    assert client.get("/register").status_code == 200
    assert client.get("/recovery").status_code == 200
    inactive = client.get("/inactive-account")
    assert inactive.status_code == 200
    assert "Contacte a la persona administradora" in inactive.text


def test_private_page_redirects_without_session(client):
    response = client.get("/workspace", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_organization_page_exposes_setup_forms(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/organization")
    assert response.status_code == 200
    assert 'data-endpoint="/academic-years"' in response.text
    assert 'id="student-form"' in response.text
    assert 'id="subject-section-form"' in response.text
    assert 'id="subject-section-subject"' in response.text
    assert 'id="subject-section-section"' in response.text


def test_task_page_exposes_creation_form(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert 'data-endpoint="/tasks"' in response.text
    assert 'name="due_on"' in response.text
    assert 'id="roster-form"' in response.text
    assert 'id="task-edit-form"' in response.text
    assert 'id="roster-task-id"' in response.text


def test_report_page_exposes_historical_scope(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/reports")
    assert response.status_code == 200
    assert 'id="report-year-id"' in response.text


def test_follow_up_page_exposes_year_scope(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/follow-up")
    assert response.status_code == 200
    assert '<select id="follow-up-year">' in response.text
    years = client.get("/academic-years")
    assert years.status_code == 200
    assert years.json() == []


def test_student_profile_page_is_protected_and_exposes_profile_target(client, unique_email):
    response = client.get("/students/00000000-0000-0000-0000-000000000000", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/students/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 200
    assert 'id="student-profile"' in response.text
    assert 'data-profile-url="/students/00000000-0000-0000-0000-000000000000/profile"' in response.text


def test_organization_options_are_tenant_scoped(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/organization/options")
    assert response.status_code == 200
    assert response.json() == {"years": [], "subjects": [], "sections": []}


def test_organization_page_exposes_import_preview(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    response = client.get("/organization")
    assert response.status_code == 200
    assert 'id="import-form"' in response.text
    assert 'id="import-commit"' in response.text
