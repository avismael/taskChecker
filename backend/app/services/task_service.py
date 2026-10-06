from datetime import date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.persistence.models.delivery import (
    Delivery,
    DeliveryStatus,
    Evidence,
    PrivateObservation,
)
from backend.app.persistence.models.organization import (
    AcademicYear,
    Section,
    Student,
    StudentMembership,
    Subject,
    SubjectSection,
)
from backend.app.persistence.models.task import Task
from backend.app.services.audit_service import audit


def create_task(
    session: Session,
    tenant_id: UUID,
    academic_year_id: UUID,
    subject_id: UUID,
    section_id: UUID,
    title: str,
    description: str,
    assigned_on: date,
    due_on: date,
    actor_id: UUID | None = None,
) -> Task:
    if due_on < assigned_on:
        raise ValueError("Due date cannot precede assignment date.")
    references = (
        session.scalar(select(AcademicYear).where(AcademicYear.id == academic_year_id, AcademicYear.tenant_id == tenant_id)),
        session.scalar(select(Subject).where(Subject.id == subject_id, Subject.tenant_id == tenant_id)),
        session.scalar(select(Section).where(Section.id == section_id, Section.tenant_id == tenant_id)),
    )
    if any(reference is None for reference in references):
        raise ValueError("Academic organization does not belong to this tenant.")
    if session.scalar(
        select(SubjectSection).where(
            SubjectSection.tenant_id == tenant_id,
            SubjectSection.subject_id == subject_id,
            SubjectSection.section_id == section_id,
        )
    ) is None:
        raise ValueError("La asignatura no está vinculada a la sección seleccionada.")
    task = Task(
        tenant_id=tenant_id,
        academic_year_id=academic_year_id,
        subject_id=subject_id,
        section_id=section_id,
        title=title.strip(),
        description=description,
        assigned_on=assigned_on,
        due_on=due_on,
    )
    session.add(task)
    session.flush()
    members = session.scalars(
        select(StudentMembership).where(
            StudentMembership.tenant_id == tenant_id,
            StudentMembership.academic_year_id == academic_year_id,
            StudentMembership.section_id == section_id,
        )
    )
    now = datetime.now().astimezone()
    for member in members:
        session.add(
            Delivery(
                tenant_id=tenant_id,
                task_id=task.id,
                student_id=member.student_id,
                status=DeliveryStatus.PENDING,
                created_at=now,
                updated_at=now,
            )
        )
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="task",
        resource_id=str(task.id),
        action="created",
        new_values={"title": task.title, "academic_year_id": str(academic_year_id)},
    )
    session.commit()
    session.refresh(task)
    return task


def get_task(session: Session, tenant_id: UUID, task_id: UUID) -> Task:
    task = session.scalar(select(Task).where(Task.id == task_id, Task.tenant_id == tenant_id))
    if task is None:
        raise ValueError("Task not found.")
    return task


def update_task(
    session: Session,
    tenant_id: UUID,
    task_id: UUID,
    actor_id: UUID | None = None,
    *,
    title: str | None = None,
    description: str | None = None,
    assigned_on: date | None = None,
    due_on: date | None = None,
    archived: bool | None = None,
) -> Task:
    task = get_task(session, tenant_id, task_id)
    next_assigned_on = assigned_on if assigned_on is not None else task.assigned_on
    next_due_on = due_on if due_on is not None else task.due_on
    if next_due_on < next_assigned_on:
        raise ValueError("Due date cannot precede assignment date.")
    previous_values = {
        "title": task.title,
        "description": task.description,
        "assigned_on": task.assigned_on.isoformat(),
        "due_on": task.due_on.isoformat(),
        "archived": task.archived,
    }
    if title is not None:
        task.title = title.strip()
    if description is not None:
        task.description = description
    if assigned_on is not None:
        task.assigned_on = assigned_on
    if due_on is not None:
        task.due_on = due_on
    if archived is not None:
        task.archived = archived
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="task",
        resource_id=str(task.id),
        action="updated" if archived is None else "archived" if archived else "unarchived",
        previous_values=previous_values,
        new_values={
            "title": task.title,
            "description": task.description,
            "assigned_on": task.assigned_on.isoformat(),
            "due_on": task.due_on.isoformat(),
            "archived": task.archived,
        },
    )
    session.commit()
    session.refresh(task)
    return task


def list_tasks(session: Session, tenant_id: UUID) -> list[Task]:
    return list(
        session.scalars(
            select(Task)
            .where(Task.tenant_id == tenant_id, Task.archived.is_(False))
            .order_by(Task.due_on, Task.title)
        )
    )


def task_roster(session: Session, tenant_id: UUID, task_id: UUID):
    get_task(session, tenant_id, task_id)
    rows = list(
        session.execute(
            select(Delivery, Student)
            .join(Student, Student.id == Delivery.student_id)
            .where(
                Delivery.task_id == task_id,
                Delivery.tenant_id == tenant_id,
                Student.tenant_id == tenant_id,
            )
        )
    )
    return [
        {
            "delivery": delivery,
            "student": student,
            "evidence_count": session.scalar(
                select(func.count(Evidence.id)).where(
                    Evidence.delivery_id == delivery.id, Evidence.tenant_id == tenant_id
                )
            )
            or 0,
            "observations": list(
                session.scalars(
                    select(PrivateObservation)
                    .where(
                        PrivateObservation.delivery_id == delivery.id,
                        PrivateObservation.tenant_id == tenant_id,
                    )
                    .order_by(PrivateObservation.created_at.desc())
                )
            ),
        }
        for delivery, student in rows
    ]
