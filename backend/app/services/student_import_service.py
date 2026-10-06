import csv
import io
from dataclasses import dataclass
from uuid import UUID

from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.observability.logging import log_event
from backend.app.persistence.models.organization import Student, StudentMembership
from backend.app.services.audit_service import audit


@dataclass(frozen=True)
class ImportRow:
    row_number: int
    nie: str
    first_name: str
    last_name: str
    errors: tuple[str, ...]


def parse_student_import(filename: str, content: bytes) -> list[ImportRow]:
    if filename.casefold().endswith(".csv"):
        rows = list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    elif filename.casefold().endswith(".xlsx"):
        workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        sheet = workbook.active
        values = list(sheet.values)
        headers = [str(value).strip().casefold() if value is not None else "" for value in values[0]]
        rows = [dict(zip(headers, row, strict=False)) for row in values[1:]]
    else:
        raise ValueError("Only CSV and XLSX imports are supported.")

    seen: set[str] = set()
    result = []
    for number, row in enumerate(rows, start=2):
        nie = str(row.get("nie") or "").strip().upper()
        first_name = str(row.get("nombre") or row.get("first_name") or "").strip()
        last_name = str(row.get("apellido") or row.get("last_name") or "").strip()
        errors = []
        if not nie:
            errors.append("NIE is required")
        if not first_name:
            errors.append("First name is required")
        if not last_name:
            errors.append("Last name is required")
        if nie in seen:
            errors.append("Duplicate NIE in import")
        if nie:
            seen.add(nie)
        result.append(ImportRow(number, nie, first_name, last_name, tuple(errors)))
    return result


def commit_student_import(
    session: Session,
    tenant_id: UUID,
    academic_year_id: UUID,
    section_id: UUID,
    rows: list[ImportRow],
    actor_id: UUID,
) -> int:
    if any(row.errors for row in rows):
        raise ValueError("Import contains validation errors and cannot be committed.")
    imported = 0
    for row in rows:
        exists = session.scalar(
            select(Student).where(Student.tenant_id == tenant_id, Student.nie == row.nie)
        )
        if exists:
            raise ValueError(f"A student with NIE {row.nie} already exists.")
        student = Student(
            tenant_id=tenant_id,
            nie=row.nie,
            first_name=row.first_name,
            last_name=row.last_name,
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
        imported += 1
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="student_import",
        resource_id=str(tenant_id),
        action="committed",
        new_values={"count": imported, "academic_year_id": str(academic_year_id)},
    )
    session.commit()
    log_event(
        "student_import_committed",
        tenant_id=str(tenant_id),
        count=imported,
        academic_year_id=str(academic_year_id),
    )
    return imported
