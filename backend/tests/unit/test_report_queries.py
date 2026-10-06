from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from backend.app.persistence.models.delivery import DeliveryStatus
from backend.app.services.report_service import (
    csv_bytes,
    delivery_report,
    pdf_bytes,
    print_html,
    xlsx_bytes,
)


def test_empty_report_is_valid_csv():
    assert b"student,nie,task,status" in csv_bytes([])


def test_xlsx_and_print_outputs_are_renderable():
    rows = [{"student": "<Student>", "status": "pending"}]
    assert xlsx_bytes(rows).startswith(b"PK")
    assert "&lt;Student&gt;" in print_html("Report", rows)
    assert pdf_bytes("Report", rows).startswith(b"%PDF")


def test_delivery_report_has_no_grading_fields():
    tenant_id = uuid4()
    student_id = uuid4()
    academic_year_id = uuid4()
    session = Mock()
    session.execute.return_value.all.return_value = [
        (
            SimpleNamespace(status=DeliveryStatus.PENDING, actual_delivered_at=None),
            SimpleNamespace(first_name="Ana", last_name="Lopez", nie="A-001"),
            SimpleNamespace(title="First task", academic_year_id=academic_year_id),
        )
    ]

    rows = delivery_report(session, tenant_id, student_id, academic_year_id)

    statement = str(session.execute.call_args.args[0])
    assert "deliveries.tenant_id" in statement
    assert "deliveries.student_id" in statement
    assert "tasks.academic_year_id" in statement
    assert set(rows[0]) == {
        "student",
        "nie",
        "task",
        "status",
        "actual_delivered_at",
        "academic_year_id",
    }
    assert not {key.lower() for key in rows[0]} & {"grade", "score", "average"}
