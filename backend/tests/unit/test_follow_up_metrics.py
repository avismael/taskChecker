from types import SimpleNamespace
from uuid import uuid4

from backend.app.persistence.models.delivery import DeliveryStatus
from backend.app.services.follow_up_service import dashboard, student_profile


def test_dashboard_starts_with_zero_delivery_counts(session, tenant_id):
    result = dashboard(session, tenant_id)
    assert result["active_tasks"] == 0
    assert result["deliveries"]["pending"] == 0


def test_dashboard_accepts_historical_year_scope(session, tenant_id):
    result = dashboard(session, tenant_id, None)
    assert set(result["deliveries"]) >= {"pending", "completed"}


class _ProfileSession:
    def __init__(self, student, deliveries):
        self.student = student
        self.deliveries = deliveries

    def scalar(self, statement):
        return self.student

    def scalars(self, statement):
        return self.deliveries


def test_student_profile_compliance_is_based_on_completed_deliveries():
    student = SimpleNamespace(
        id=uuid4(), nie="A-001", first_name="Ana", last_name="Lopez"
    )
    deliveries = [
        SimpleNamespace(status=DeliveryStatus.COMPLETED),
        SimpleNamespace(status=DeliveryStatus.PENDING),
    ]
    result = student_profile(_ProfileSession(student, deliveries), uuid4(), student.id)

    assert result["task_count"] == 2
    assert result["counts"]["completed"] == 1
    assert result["compliance_percentage"] == 50.0


def test_student_profile_without_deliveries_has_zero_compliance():
    student = SimpleNamespace(
        id=uuid4(), nie="A-002", first_name="Luis", last_name="Sanz"
    )
    result = student_profile(_ProfileSession(student, []), uuid4(), student.id)

    assert result["task_count"] == 0
    assert result["compliance_percentage"] == 0
