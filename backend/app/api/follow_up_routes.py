from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import CurrentActor, require_teacher
from backend.app.persistence.session import get_db
from backend.app.services.follow_up_service import dashboard, search_students, student_profile

router = APIRouter(tags=["follow-up"])


@router.get("/students/{student_id}/profile")
def profile(
    student_id: UUID,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    return student_profile(session, actor.tenant_id, student_id)


@router.get("/dashboard")
def dashboard_view(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    academic_year_id: UUID | None = None,
):
    return dashboard(session, actor.tenant_id, academic_year_id)


@router.get("/today")
def today(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    academic_year_id: UUID | None = None,
):
    return {
        "dashboard": dashboard(session, actor.tenant_id, academic_year_id),
        "date": datetime.now(UTC).date().isoformat(),
    }


@router.get("/search")
def search(
    q: str = "",
    actor: Annotated[CurrentActor, Depends(require_teacher)] = None,
    session: Annotated[Session, Depends(get_db)] = None,
):
    return {"students": search_students(session, actor.tenant_id, q)}
