from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import CurrentActor, require_teacher
from backend.app.persistence.session import get_db
from backend.app.services.task_service import create_task, list_tasks, task_roster, update_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskPayload(BaseModel):
    academic_year_id: UUID
    subject_id: UUID
    section_id: UUID
    title: str
    description: str = ""
    assigned_on: date
    due_on: date


class TaskUpdatePayload(BaseModel):
    title: str | None = None
    description: str | None = None
    assigned_on: date | None = None
    due_on: date | None = None
    archived: bool | None = None


@router.post("")
def task(payload: TaskPayload, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    item = create_task(session, actor.tenant_id, actor_id=actor.account_id, **payload.model_dump())
    return {"id": str(item.id), "title": item.title, "due_on": item.due_on.isoformat()}


@router.get("/data")
def task_data(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    return [
        {
            "id": str(item.id),
            "title": item.title,
            "due_on": item.due_on.isoformat(),
        }
        for item in list_tasks(session, actor.tenant_id)
    ]


@router.patch("/{task_id}")
def update(
    task_id: UUID,
    payload: TaskUpdatePayload,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    item = update_task(
        session,
        actor.tenant_id,
        task_id,
        actor.account_id,
        **payload.model_dump(exclude_unset=True),
    )
    return {
        "id": str(item.id),
        "title": item.title,
        "description": item.description,
        "assigned_on": item.assigned_on.isoformat(),
        "due_on": item.due_on.isoformat(),
        "archived": item.archived,
    }


@router.get("/{task_id}/roster")
def roster(task_id: UUID, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    rows = task_roster(session, actor.tenant_id, task_id)
    return [
        {
            "id": str(item["delivery"].id),
            "student_id": str(item["delivery"].student_id),
            "student_name": f"{item['student'].first_name} {item['student'].last_name}".strip(),
            "student_nie": item["student"].nie,
            "status": item["delivery"].status.value,
            "actual_delivered_at": item["delivery"].actual_delivered_at.isoformat()
            if item["delivery"].actual_delivered_at
            else None,
            "evidence_count": item["evidence_count"],
            "observation_count": len(item["observations"]),
            "observation_summary": item["observations"][0].body if item["observations"] else None,
        }
        for item in rows
    ]
