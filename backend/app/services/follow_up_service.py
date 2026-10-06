from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.persistence.models.delivery import Delivery, DeliveryStatus
from backend.app.persistence.models.organization import AcademicYear, AcademicYearStatus, Student
from backend.app.persistence.models.task import Task


def student_profile(session: Session, tenant_id: UUID, student_id: UUID) -> dict:
    student = session.scalar(
        select(Student).where(Student.id == student_id, Student.tenant_id == tenant_id)
    )
    if student is None:
        raise ValueError("Student not found.")
    deliveries = list(
        session.scalars(select(Delivery).where(Delivery.student_id == student_id, Delivery.tenant_id == tenant_id))
    )
    counts = {status.value: 0 for status in DeliveryStatus}
    for delivery in deliveries:
        counts[delivery.status.value] += 1
    completed = counts[DeliveryStatus.COMPLETED.value]
    compliance = round(completed / len(deliveries) * 100, 2) if deliveries else 0
    return {
        "id": str(student.id),
        "nie": student.nie,
        "name": f"{student.first_name} {student.last_name}",
        "task_count": len(deliveries),
        "counts": counts,
        "compliance_percentage": compliance,
    }


def dashboard(session: Session, tenant_id: UUID, academic_year_id: UUID | None = None) -> dict:
    if academic_year_id is None:
        academic_year_id = session.scalar(
            select(AcademicYear.id).where(
                AcademicYear.tenant_id == tenant_id,
                AcademicYear.status == AcademicYearStatus.ACTIVE,
            )
        )
    delivery_scope = select(Delivery.id).join(Task, Task.id == Delivery.task_id).where(
        Delivery.tenant_id == tenant_id,
        Task.academic_year_id == academic_year_id,
    )
    counts = {
        status.value: session.scalar(
            select(func.count(Delivery.id)).where(
                Delivery.id.in_(delivery_scope), Delivery.status == status
            )
        )
        for status in DeliveryStatus
    }
    active_tasks = session.scalar(
        select(func.count(Task.id)).where(
            Task.tenant_id == tenant_id,
            Task.academic_year_id == academic_year_id,
            Task.archived.is_(False),
        )
    )
    return {"active_tasks": active_tasks or 0, "deliveries": counts}


def search_students(session: Session, tenant_id: UUID, query: str = "") -> list[dict]:
    normalized = query.strip()
    statement = select(Student).where(Student.tenant_id == tenant_id, Student.archived.is_(False))
    if normalized:
        pattern = f"%{normalized}%"
        statement = statement.where(
            Student.nie.ilike(pattern)
            | Student.first_name.ilike(pattern)
            | Student.last_name.ilike(pattern)
        )
    students = session.scalars(statement.order_by(Student.last_name, Student.first_name).limit(50)).all()
    return [
        {"id": str(student.id), "nie": student.nie, "name": f"{student.first_name} {student.last_name}"}
        for student in students
    ]
