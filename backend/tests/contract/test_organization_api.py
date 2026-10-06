def test_organization_options_are_scoped_and_include_created_records(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200

    year = client.post("/academic-years", json={"name": "2026"}).json()
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    link = client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    student = client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "A-001",
            "first_name": "Ana",
            "last_name": "Lopez",
        },
    )
    options = client.get("/organization/options")

    assert link.status_code == 200
    assert student.status_code == 200
    assert options.status_code == 200
    assert options.json()["years"][0]["id"] == year["id"]
    assert options.json()["subjects"][0]["id"] == subject["id"]
    assert options.json()["sections"][0]["id"] == section["id"]

    archived_subject = client.patch(f"/subjects/{subject['id']}", json={"archived": True})
    archived_section = client.patch(f"/sections/{section['id']}", json={"archived": True})
    refreshed_options = client.get("/organization/options")
    assert archived_subject.json()["archived"] is True
    assert archived_section.json()["archived"] is True
    assert refreshed_options.json()["subjects"] == []
    assert refreshed_options.json()["sections"] == []


def test_organization_mutations_require_authentication(client):
    assert client.post("/subjects", json={"name": "Computing"}).status_code == 401
    assert client.post("/sections", json={"name": "First A"}).status_code == 401
    assert client.get("/organization/options").status_code == 401


def test_subject_section_link_endpoint_is_idempotency_safe_and_clear_on_duplicate(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "safe-password"})
    client.post("/auth/login", json={"email": unique_email, "password": "safe-password"})
    subject = client.post("/subjects", json={"name": "Computing"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()

    first = client.post(f"/subjects/{subject['id']}/sections/{section['id']}")
    duplicate = client.post(f"/subjects/{subject['id']}/sections/{section['id']}")

    assert first.status_code == 200
    assert first.json() == {"subject_id": subject["id"], "section_id": section["id"]}
    assert duplicate.status_code == 422
    assert duplicate.json()["message"] == "La asignatura ya está vinculada a esta sección."


def test_student_listing_requires_authentication_and_returns_empty_list(client):
    assert client.get("/students").status_code == 401


def test_student_listing_includes_created_and_imported_students_with_filters(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200

    first_year = client.post("/academic-years", json={"name": "2026"}).json()
    first_section = client.post("/sections", json={"name": "First A"}).json()
    created = client.post(
        "/students",
        json={
            "academic_year_id": first_year["id"],
            "section_id": first_section["id"],
            "nie": "A-001",
            "first_name": "Ana",
            "last_name": "Lopez",
        },
    )
    assert client.post(f"/academic-years/{first_year['id']}/close").status_code == 200
    second_year = client.post("/academic-years", json={"name": "2027"}).json()
    second_section = client.post("/sections", json={"name": "Second B"}).json()
    imported = client.post(
        f"/students/imports/commit?academic_year_id={second_year['id']}&section_id={second_section['id']}",
        files={"file": ("students.csv", "nie,nombre,apellido\nB-002,Luis,Sanz\n", "text/csv")},
    )

    response = client.get("/students")
    first_filter = client.get(f"/students?academic_year_id={first_year['id']}")
    second_filter = client.get(f"/students?section_id={second_section['id']}")

    assert created.status_code == 200
    assert imported.status_code == 200
    assert imported.json() == {"imported": 1}
    assert response.status_code == 200
    assert [student["nie"] for student in response.json()] == ["A-001", "B-002"]
    assert response.json()[0]["name"] == "Ana Lopez"
    assert len(response.json()) == 2
    assert [student["nie"] for student in first_filter.json()] == ["A-001"]
    assert [student["nie"] for student in second_filter.json()] == ["B-002"]

    transferred = client.patch(
        f"/students/{created.json()['id']}/membership",
        json={"academic_year_id": second_year["id"], "section_id": second_section["id"]},
    )
    assert transferred.status_code == 200
    assert len([student for student in client.get("/students").json() if student["nie"] == "A-001"]) == 1


def test_student_listing_is_tenant_scoped(client, unique_email):
    assert client.post(
        "/auth/register", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": unique_email, "password": "safe-password"}
    ).status_code == 200
    year = client.post("/academic-years", json={"name": "2026"}).json()
    section = client.post("/sections", json={"name": "First A"}).json()
    client.post(
        "/students",
        json={
            "academic_year_id": year["id"],
            "section_id": section["id"],
            "nie": "PRIVATE-001",
            "first_name": "Private",
            "last_name": "Student",
        },
    )

    other_email = f"other-{unique_email}"
    assert client.post(
        "/auth/register", json={"email": other_email, "password": "safe-password"}
    ).status_code == 201
    assert client.post(
        "/auth/login", json={"email": other_email, "password": "safe-password"}
    ).status_code == 200

    assert client.get("/students").json() == []
