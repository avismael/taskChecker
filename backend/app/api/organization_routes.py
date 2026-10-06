from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import CurrentActor, require_teacher
from backend.app.api.security import enforce_rate_limit, read_upload
from backend.app.config import get_settings
from backend.app.persistence.models.organization import (
    AcademicYear,
    MembershipStatus,
    Section,
    Student,
    StudentMembership,
    Subject,
)
from backend.app.persistence.session import get_db
from backend.app.services.organization_service import (
    archive_section,
    archive_subject,
    close_year,
    create_section,
    create_subject,
    create_year,
    link_subject_section,
)
from backend.app.services.student_import_service import commit_student_import, parse_student_import
from backend.app.services.student_service import create_student, transfer_student

router = APIRouter(tags=["organization"])


class NamePayload(BaseModel):
    name: str
    description: str | None = None


class ArchivePayload(BaseModel):
    archived: bool


class StudentPayload(BaseModel):
    academic_year_id: UUID
    section_id: UUID
    nie: str
    first_name: str
    last_name: str


class StudentTransferPayload(BaseModel):
    academic_year_id: UUID
    section_id: UUID


@router.post("/academic-years")
def academic_year(payload: NamePayload, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    year = create_year(session, actor.tenant_id, payload.name, actor.account_id)
    return {"id": str(year.id), "label": year.label, "status": year.status.value}


@router.get("/academic-years")
def academic_years(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    years = session.scalars(
        select(AcademicYear)
        .where(AcademicYear.tenant_id == actor.tenant_id)
        .order_by(AcademicYear.starts_on.desc().nullslast(), AcademicYear.label.desc())
    ).all()
    return [{"id": str(year.id), "label": year.label, "status": year.status.value} for year in years]


@router.get("/organization/options")
def organization_options(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    years = session.scalars(select(AcademicYear).where(AcademicYear.tenant_id == actor.tenant_id)).all()
    subjects = session.scalars(
        select(Subject).where(Subject.tenant_id == actor.tenant_id, Subject.archived.is_(False))
    ).all()
    sections = session.scalars(
        select(Section).where(Section.tenant_id == actor.tenant_id, Section.archived.is_(False))
    ).all()
    return {
        "years": [{"id": str(item.id), "label": item.label} for item in years],
        "subjects": [{"id": str(item.id), "label": item.name} for item in subjects],
        "sections": [{"id": str(item.id), "label": item.name} for item in sections],
    }


@router.post("/academic-years/{year_id}/close")
def academic_year_close(year_id: UUID, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    year = close_year(session, actor.tenant_id, year_id, actor.account_id)
    return {"id": str(year.id), "status": year.status.value, "closed_at": str(year.closed_at)}


@router.post("/subjects")
def subject(payload: NamePayload, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    item = create_subject(session, actor.tenant_id, payload.name, payload.description, actor.account_id)
    return {"id": str(item.id), "name": item.name}


@router.post("/sections")
def section(payload: NamePayload, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    item = create_section(session, actor.tenant_id, payload.name, actor.account_id)
    return {"id": str(item.id), "name": item.name}


@router.patch("/subjects/{subject_id}")
def subject_archive(
    subject_id: UUID,
    payload: ArchivePayload,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    item = archive_subject(session, actor.tenant_id, subject_id, payload.archived, actor.account_id)
    return {"id": str(item.id), "name": item.name, "archived": item.archived}


@router.patch("/sections/{section_id}")
def section_archive(
    section_id: UUID,
    payload: ArchivePayload,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    item = archive_section(session, actor.tenant_id, section_id, payload.archived, actor.account_id)
    return {"id": str(item.id), "name": item.name, "archived": item.archived}


@router.post("/subjects/{subject_id}/sections/{section_id}")
def subject_section(subject_id: UUID, section_id: UUID, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    link_subject_section(session, actor.tenant_id, subject_id, section_id, actor.account_id)
    return {"subject_id": str(subject_id), "section_id": str(section_id)}


@router.post("/students")
def student(payload: StudentPayload, actor: Annotated[CurrentActor, Depends(require_teacher)], session: Annotated[Session, Depends(get_db)]):
    item = create_student(session, actor.tenant_id, actor_id=actor.account_id, **payload.model_dump())
    return {"id": str(item.id), "nie": item.nie, "name": f"{item.first_name} {item.last_name}"}


@router.get("/students")
def students(
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    academic_year_id: UUID | None = None,
    section_id: UUID | None = None,
):
    memberships = (
        select(
            StudentMembership.student_id,
            StudentMembership.academic_year_id,
            StudentMembership.section_id,
            AcademicYear.label.label("academic_year"),
            Section.name.label("section"),
            func.row_number()
            .over(
                partition_by=StudentMembership.student_id,
                order_by=(StudentMembership.created_at.desc(), StudentMembership.id.desc()),
            )
            .label("membership_rank"),
        )
        .join(
            AcademicYear,
            (AcademicYear.id == StudentMembership.academic_year_id)
            & (AcademicYear.tenant_id == StudentMembership.tenant_id),
        )
        .join(
            Section,
            (Section.id == StudentMembership.section_id)
            & (Section.tenant_id == StudentMembership.tenant_id),
        )
        .where(
            StudentMembership.tenant_id == actor.tenant_id,
            StudentMembership.status == MembershipStatus.ACTIVE,
        )
    )
    if academic_year_id is not None:
        memberships = memberships.where(StudentMembership.academic_year_id == academic_year_id)
    if section_id is not None:
        memberships = memberships.where(StudentMembership.section_id == section_id)

    active_membership = memberships.subquery()
    rows = session.execute(
        select(
            Student,
            active_membership.c.academic_year_id,
            active_membership.c.section_id,
            active_membership.c.academic_year,
            active_membership.c.section,
        )
        .join(
            active_membership,
            (active_membership.c.student_id == Student.id)
            & (active_membership.c.membership_rank == 1),
        )
        .where(Student.tenant_id == actor.tenant_id, Student.archived.is_(False))
        .order_by(Student.last_name, Student.first_name, Student.nie)
    ).all()
    return [
        {
            "id": str(item.id),
            "nie": item.nie,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "name": f"{item.first_name} {item.last_name}",
            "academic_year_id": str(academic_year_id),
            "section_id": str(section_id),
            "academic_year": academic_year,
            "section": section,
        }
        for item, academic_year_id, section_id, academic_year, section in rows
    ]


@router.patch("/students/{student_id}/membership")
def student_membership(
    student_id: UUID,
    payload: StudentTransferPayload,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    membership = transfer_student(
        session,
        actor.tenant_id,
        student_id,
        payload.academic_year_id,
        payload.section_id,
        actor.account_id,
    )
    return {
        "id": str(membership.id),
        "student_id": str(membership.student_id),
        "academic_year_id": str(membership.academic_year_id),
        "section_id": str(membership.section_id),
        "status": membership.status.value,
    }


@router.post("/students/imports/preview")
async def student_import_preview(
    request: Request,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    file: UploadFile = File(...),
):
    enforce_rate_limit(request, "student-import", get_settings().auth_rate_limit)
    del actor
    rows = parse_student_import(file.filename or "", await read_upload(file, get_settings().max_upload_bytes))
    return {
        "filename": file.filename,
        "rows": [
            {
                "row_number": row.row_number,
                "nie": row.nie,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "errors": list(row.errors),
            }
            for row in rows
        ],
        "critical_errors": sum(bool(row.errors) for row in rows),
    }


@router.post("/students/imports/commit")
async def student_import_commit(
    request: Request,
    academic_year_id: UUID,
    section_id: UUID,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    enforce_rate_limit(request, "student-import", get_settings().auth_rate_limit)
    rows = parse_student_import(file.filename or "", await read_upload(file, get_settings().max_upload_bytes))
    imported = commit_student_import(
        session,
        actor.tenant_id,
        academic_year_id,
        section_id,
        rows,
        actor.account_id,
    )
    return {"imported": imported}
