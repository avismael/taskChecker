import pytest

from backend.app.persistence.models.organization import AcademicYearStatus
from backend.app.services.organization_service import close_year, create_section, create_year
from backend.app.services.student_service import create_student, transfer_student


def test_only_one_active_year_is_allowed(session, tenant_id):
    create_year(session, tenant_id, "2026")
    with pytest.raises(ValueError, match="Only one academic year"):
        create_year(session, tenant_id, "2027")


def test_closing_year_sets_closed_status_and_date(session, tenant_id):
    year = create_year(session, tenant_id, "2026")

    closed = close_year(session, tenant_id, year.id)

    assert closed.status == AcademicYearStatus.CLOSED
    assert closed.closed_at is not None


def test_student_membership_can_be_transferred_within_year(session, tenant_id):
    year = create_year(session, tenant_id, "2026")
    first_section = create_section(session, tenant_id, "First A")
    second_section = create_section(session, tenant_id, "First B")
    student = create_student(session, tenant_id, year.id, first_section.id, "A-001", "Ana", "Lopez")

    membership = transfer_student(session, tenant_id, student.id, year.id, second_section.id)

    assert membership.section_id == second_section.id


def test_student_nie_is_unique_per_tenant(session, tenant_id):
    year = create_year(session, tenant_id, "2026")
    section = create_section(session, tenant_id, "First A")
    create_student(session, tenant_id, year.id, section.id, " a-001 ", "Ana", "Lopez")

    with pytest.raises(ValueError, match="NIE already exists"):
        create_student(session, tenant_id, year.id, section.id, "A-001", "Another", "Student")
