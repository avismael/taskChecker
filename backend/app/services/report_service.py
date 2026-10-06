import csv
import html
import io
from uuid import UUID

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.persistence.models.delivery import Delivery
from backend.app.persistence.models.organization import Student
from backend.app.persistence.models.task import Task


def delivery_report(
    session: Session,
    tenant_id: UUID,
    student_id: UUID | None = None,
    academic_year_id: UUID | None = None,
) -> list[dict]:
    statement = (
        select(Delivery, Student, Task)
        .join(Student, Student.id == Delivery.student_id)
        .join(Task, Task.id == Delivery.task_id)
        .where(Delivery.tenant_id == tenant_id)
    )
    if student_id:
        statement = statement.where(Delivery.student_id == student_id)
    if academic_year_id:
        statement = statement.where(Task.academic_year_id == academic_year_id)
    rows = session.execute(statement).all()
    return [
        {
            "student": f"{student.first_name} {student.last_name}",
            "nie": student.nie,
            "task": task.title,
            "status": delivery.status.value,
            "actual_delivered_at": str(delivery.actual_delivered_at),
            "academic_year_id": str(task.academic_year_id),
        }
        for delivery, student, task in rows
    ]


def csv_bytes(rows: list[dict]) -> bytes:
    output = io.StringIO()
    fieldnames = list(rows[0]) if rows else ["student", "nie", "task", "status"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def xlsx_bytes(rows: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    fieldnames = list(rows[0]) if rows else ["student", "nie", "task", "status"]
    sheet.append(fieldnames)
    for row in rows:
        sheet.append([row.get(field) for field in fieldnames])
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def print_html(title: str, rows: list[dict]) -> str:
    headers = list(rows[0]) if rows else ["student", "nie", "task", "status"]
    table_headers = "".join(f"<th>{html.escape(str(header))}</th>" for header in headers)
    table_rows = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row.get(header, '')))}</td>" for header in headers)
        + "</tr>"
        for row in rows
    )
    safe_title = html.escape(title)
    return f"<html><head><title>{safe_title}</title></head><body><h1>{safe_title}</h1><table><thead><tr>{table_headers}</tr></thead><tbody>{table_rows}</tbody></table></body></html>"


def pdf_bytes(title: str, rows: list[dict]) -> bytes:
    output = io.BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, title=title)
    headers = list(rows[0]) if rows else ["student", "nie", "task", "status"]
    data = [headers] + [[str(row.get(header, "")) for header in headers] for row in rows]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d2939")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c9c0b2")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    document.build([table])
    return output.getvalue()
