from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import CurrentActor, require_teacher
from backend.app.persistence.session import get_db
from backend.app.services.report_outputs import report_output
from backend.app.services.report_service import delivery_report

router = APIRouter(prefix="/reports", tags=["reports"])


def render_report(report_type: str, rows: list[dict], format: str):
    return report_output.render(report_type, rows, format)


@router.get("/individual/{student_id}")
def individual(
    student_id: UUID,
    format: str = "json",
    academic_year_id: UUID | None = None,
    actor: Annotated[CurrentActor, Depends(require_teacher)] = None,
    session: Annotated[Session, Depends(get_db)] = None,
):
    rows = delivery_report(session, actor.tenant_id, student_id, academic_year_id)
    return render_report("individual", rows, format)


@router.get("/section")
def section_report(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    format: str = "json",
    academic_year_id: UUID | None = None,
):
    return render_report("section", delivery_report(session, actor.tenant_id, academic_year_id=academic_year_id), format)


@router.get("/pending")
def pending_report(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    format: str = "json",
    academic_year_id: UUID | None = None,
):
    rows = delivery_report(session, actor.tenant_id, academic_year_id=academic_year_id)
    return render_report("pending", [row for row in rows if row["status"] in {"pending", "not_delivered"}], format)


@router.get("/compliance")
def compliance_report(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    format: str = "json",
    academic_year_id: UUID | None = None,
):
    return render_report("compliance", delivery_report(session, actor.tenant_id, academic_year_id=academic_year_id), format)
