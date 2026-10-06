from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.persistence.models.organization import (
    AcademicYear,
    AcademicYearStatus,
    Section,
    Subject,
    SubjectSection,
)
from backend.app.services.audit_service import audit


def create_year(session: Session, tenant_id: UUID, label: str, actor_id: UUID | None = None) -> AcademicYear:
    if session.scalar(
        select(AcademicYear).where(
            AcademicYear.tenant_id == tenant_id,
            AcademicYear.status == AcademicYearStatus.ACTIVE,
        )
    ):
        raise ValueError("Only one academic year may be active for a teacher.")
    year = AcademicYear(tenant_id=tenant_id, label=label, status=AcademicYearStatus.ACTIVE)
    session.add(year)
    session.flush()
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="academic_year",
        resource_id=str(year.id),
        action="created",
        new_values={"label": label},
    )
    session.commit()
    session.refresh(year)
    return year


def close_year(session: Session, tenant_id: UUID, year_id: UUID, actor_id: UUID | None = None) -> AcademicYear:
    year = session.scalar(
        select(AcademicYear).where(AcademicYear.id == year_id, AcademicYear.tenant_id == tenant_id)
    )
    if year is None:
        raise ValueError("Academic year not found.")
    if year.status == AcademicYearStatus.CLOSED:
        return year
    year.status = AcademicYearStatus.CLOSED
    year.closed_at = datetime.now(UTC).date()
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="academic_year",
        resource_id=str(year.id),
        action="closed",
        previous_values={"status": AcademicYearStatus.ACTIVE.value},
        new_values={"status": AcademicYearStatus.CLOSED.value},
    )
    session.commit()
    return year


def create_subject(session: Session, tenant_id: UUID, name: str, description: str | None, actor_id: UUID | None = None) -> Subject:
    subject = Subject(tenant_id=tenant_id, name=name.strip(), description=description)
    session.add(subject)
    session.flush()
    audit(session, tenant_id=tenant_id, actor_account_id=actor_id, resource_type="subject", resource_id=str(subject.id), action="created", new_values={"name": subject.name})
    session.commit()
    session.refresh(subject)
    return subject


def create_section(session: Session, tenant_id: UUID, name: str, actor_id: UUID | None = None) -> Section:
    section = Section(tenant_id=tenant_id, name=name.strip())
    session.add(section)
    session.flush()
    audit(session, tenant_id=tenant_id, actor_account_id=actor_id, resource_type="section", resource_id=str(section.id), action="created", new_values={"name": section.name})
    session.commit()
    session.refresh(section)
    return section


def archive_subject(
    session: Session,
    tenant_id: UUID,
    subject_id: UUID,
    archived: bool,
    actor_id: UUID | None = None,
) -> Subject:
    subject = session.scalar(select(Subject).where(Subject.id == subject_id, Subject.tenant_id == tenant_id))
    if subject is None:
        raise ValueError("Subject not found.")
    subject.archived = archived
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="subject",
        resource_id=str(subject.id),
        action="archived" if archived else "unarchived",
        new_values={"archived": archived},
    )
    session.commit()
    session.refresh(subject)
    return subject


def archive_section(
    session: Session,
    tenant_id: UUID,
    section_id: UUID,
    archived: bool,
    actor_id: UUID | None = None,
) -> Section:
    section = session.scalar(select(Section).where(Section.id == section_id, Section.tenant_id == tenant_id))
    if section is None:
        raise ValueError("Section not found.")
    section.archived = archived
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="section",
        resource_id=str(section.id),
        action="archived" if archived else "unarchived",
        new_values={"archived": archived},
    )
    session.commit()
    session.refresh(section)
    return section


def link_subject_section(session: Session, tenant_id: UUID, subject_id: UUID, section_id: UUID, actor_id: UUID | None = None):
    if not session.scalar(select(Subject).where(Subject.id == subject_id, Subject.tenant_id == tenant_id)) or not session.scalar(
        select(Section).where(Section.id == section_id, Section.tenant_id == tenant_id)
    ):
        raise ValueError("Academic organization does not belong to this tenant.")
    if session.scalar(
        select(SubjectSection).where(
            SubjectSection.tenant_id == tenant_id,
            SubjectSection.subject_id == subject_id,
            SubjectSection.section_id == section_id,
        )
    ):
        raise ValueError("La asignatura ya está vinculada a esta sección.")
    link = SubjectSection(
        tenant_id=tenant_id, subject_id=subject_id, section_id=section_id
    )
    session.add(link)
    audit(session, tenant_id=tenant_id, actor_account_id=actor_id, resource_type="subject_section", resource_id=f"{subject_id}:{section_id}", action="created")
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ValueError("La asignatura ya está vinculada a esta sección.") from error
    return link
