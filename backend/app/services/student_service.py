from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.persistence.models.organization import (
    AcademicYear,
    MembershipStatus,
    Section,
    Student,
    StudentMembership,
)
from backend.app.services.audit_service import audit


def create_student(
    session: Session,
    tenant_id: UUID,
    academic_year_id: UUID,
    section_id: UUID,
    nie: str,
    first_name: str,
    last_name: str,
    actor_id: UUID | None = None,
) -> Student:
    normalized_nie = nie.strip().upper()
    if not normalized_nie or not first_name.strip() or not last_name.strip():
        raise ValueError("NIE, first name, and last name are required.")
    if not session.scalar(
        select(AcademicYear).where(AcademicYear.id == academic_year_id, AcademicYear.tenant_id == tenant_id)
    ) or not session.scalar(
        select(Section).where(Section.id == section_id, Section.tenant_id == tenant_id)
    ):
        raise ValueError("Academic organization does not belong to this tenant.")
    if session.scalar(
        select(Student).where(Student.tenant_id == tenant_id, Student.nie == normalized_nie)
    ):
        raise ValueError("A student with this NIE already exists.")
    student = Student(
        tenant_id=tenant_id,
        nie=normalized_nie,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
    )
    session.add(student)
    session.flush()
    session.add(
        StudentMembership(
            tenant_id=tenant_id,
            student_id=student.id,
            section_id=section_id,
            academic_year_id=academic_year_id,
        )
    )
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="student",
        resource_id=str(student.id),
        action="created",
        new_values={"nie": student.nie, "academic_year_id": str(academic_year_id)},
    )
    session.commit()
    session.refresh(student)
    return student


def transfer_student(
    session: Session,
    tenant_id: UUID,
    student_id: UUID,
    academic_year_id: UUID,
    section_id: UUID,
    actor_id: UUID | None = None,
) -> StudentMembership:
    student = session.scalar(select(Student).where(Student.id == student_id, Student.tenant_id == tenant_id))
    year = session.scalar(
        select(AcademicYear).where(AcademicYear.id == academic_year_id, AcademicYear.tenant_id == tenant_id)
    )
    section = session.scalar(select(Section).where(Section.id == section_id, Section.tenant_id == tenant_id))
    if not student or not year or not section:
        raise ValueError("Student or academic organization does not belong to this tenant.")
    membership = session.scalar(
        select(StudentMembership).where(
            StudentMembership.student_id == student_id,
            StudentMembership.academic_year_id == academic_year_id,
            StudentMembership.tenant_id == tenant_id,
        )
    )
    if membership is None:
        membership = StudentMembership(
            tenant_id=tenant_id,
            student_id=student_id,
            academic_year_id=academic_year_id,
            section_id=section_id,
            status=MembershipStatus.ACTIVE,
        )
        session.add(membership)
    else:
        membership.section_id = section_id
        membership.status = MembershipStatus.ACTIVE
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="student_membership",
        resource_id=str(membership.id),
        action="transferred",
        new_values={"student_id": str(student_id), "academic_year_id": str(academic_year_id), "section_id": str(section_id)},
    )
    session.commit()
    session.refresh(membership)
    return membership
