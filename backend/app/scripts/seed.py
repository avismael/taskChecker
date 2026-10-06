import json
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.persistence.models import (
    AcademicYear,
    Delivery,
    Evidence,
    PrivateObservation,
    Section,
    Student,
    StudentMembership,
    Subject,
    SubjectSection,
    Task,
    TeacherAccount,
    Tenant,
)
from backend.app.persistence.models.account import AccountRole, AccountStatus
from backend.app.persistence.models.delivery import DeliveryStatus
from backend.app.persistence.models.organization import AcademicYearStatus, MembershipStatus
from backend.app.persistence.session import SessionLocal
from backend.app.services.auth_service import hash_password

SEED_EMAIL = "seed.teacher@taskchecker.local"
SEED_PASSWORD = "taskchecker-dev-password"
DATA_DIR = Path(__file__).resolve().parent / "seed_data"


class SeedDataError(ValueError):
    """Raised when versioned seed data is malformed or inconsistent."""


def _read_json(name: str):
    path = DATA_DIR / name
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise SeedDataError(f"No se pudo leer el archivo de seed {path}: {error}") from error


def validate_seed_data(data: dict) -> dict:
    required = ("catalog", "students", "tasks", "delivery_states", "fixtures")
    missing = [name for name in required if name not in data]
    if missing:
        raise SeedDataError(f"Faltan secciones de datos de seed: {', '.join(missing)}")
    if not isinstance(data["catalog"], dict):
        raise SeedDataError("La sección catalog debe ser un objeto JSON")
    for name in ("students", "tasks", "delivery_states"):
        if not isinstance(data[name], list) or not data[name]:
            raise SeedDataError(f"La sección {name} debe ser una lista no vacía")
    if not isinstance(data["fixtures"], dict):
        raise SeedDataError("La sección fixtures debe ser un objeto JSON")

    catalog = data["catalog"]
    for key in ("tenant_name", "academic_year", "subjects", "section"):
        if key not in catalog:
            raise SeedDataError(f"Falta catalog.{key}")
    academic_year = catalog["academic_year"]
    for key in ("label", "starts_on", "ends_on"):
        if key not in academic_year:
            raise SeedDataError(f"Falta catalog.academic_year.{key}")
    try:
        date.fromisoformat(academic_year["starts_on"])
        date.fromisoformat(academic_year["ends_on"])
    except (TypeError, ValueError) as error:
        raise SeedDataError("Las fechas del año académico deben usar formato ISO") from error
    if not isinstance(catalog["subjects"], list) or not catalog["subjects"]:
        raise SeedDataError("catalog.subjects debe ser una lista no vacía")

    students = data["students"]
    student_nies = set()
    for student in students:
        _require_keys(student, ("nie", "first_name", "last_name"), "students")
        if student["nie"] in student_nies:
            raise SeedDataError(f"NIE de estudiante duplicado: {student['nie']}")
        student_nies.add(student["nie"])

    tasks = data["tasks"]
    task_titles = set()
    for task in tasks:
        _require_keys(task, ("title", "description", "subject", "assigned_on", "due_on"), "tasks")
        if task["title"] in task_titles:
            raise SeedDataError(f"Título de tarea duplicado: {task['title']}")
        if task["subject"] not in catalog["subjects"]:
            raise SeedDataError(f"Asignatura desconocida en tasks: {task['subject']}")
        try:
            date.fromisoformat(task["assigned_on"])
            date.fromisoformat(task["due_on"])
        except (TypeError, ValueError) as error:
            raise SeedDataError(f"Fechas inválidas en la tarea {task['title']}") from error
        task_titles.add(task["title"])

    if len(data["delivery_states"]) != len(students) * len(tasks):
        raise SeedDataError("delivery_states debe contener un estado por cada tarea y estudiante")
    delivery_keys = set()
    for delivery in data["delivery_states"]:
        _require_keys(delivery, ("task", "student", "status"), "delivery_states")
        key = (delivery["task"], delivery["student"])
        if key in delivery_keys or delivery["task"] not in task_titles or delivery["student"] not in student_nies:
            raise SeedDataError(f"Referencia de entrega inválida o duplicada: {key}")
        if delivery["status"] not in {status.value for status in DeliveryStatus}:
            raise SeedDataError(f"Estado de entrega desconocido: {delivery['status']}")
        if delivery.get("delivered_at"):
            try:
                datetime.fromisoformat(delivery["delivered_at"])
            except (TypeError, ValueError) as error:
                raise SeedDataError(f"Fecha de entrega inválida para {key}") from error
        delivery_keys.add(key)
    for fixture_name in ("evidence", "private_observation"):
        _require_keys(data["fixtures"], (fixture_name,), "fixtures")
        fixture_keys = ("task", "student", "kind", "url") if fixture_name == "evidence" else ("task", "student", "body")
        _require_keys(data["fixtures"][fixture_name], fixture_keys, f"fixtures.{fixture_name}")
        fixture = data["fixtures"][fixture_name]
        if fixture["task"] not in task_titles or fixture["student"] not in student_nies:
            raise SeedDataError(f"Referencia inválida en fixtures.{fixture_name}")
    return data


def _require_keys(value: dict, keys: tuple[str, ...], section: str) -> None:
    if not isinstance(value, dict) or any(key not in value for key in keys):
        raise SeedDataError(f"Cada elemento de {section} requiere: {', '.join(keys)}")


def load_seed_data() -> dict:
    data = {
        "catalog": _read_json("catalog.json"),
        "students": _read_json("students.json"),
        "tasks": _read_json("tasks.json"),
        "delivery_states": _read_json("delivery_states.json"),
        "fixtures": _read_json("fixtures.json"),
    }
    return validate_seed_data(data)


def _one(session: Session, model, **filters):
    return session.scalar(select(model).filter_by(**filters))


def _get_or_create_delivery(session, tenant_id, task_id, student_id, status, delivered_at):
    delivery = _one(session, Delivery, tenant_id=tenant_id, task_id=task_id, student_id=student_id)
    now = datetime.now(UTC)
    if delivery is None:
        delivery = Delivery(tenant_id=tenant_id, task_id=task_id, student_id=student_id, created_at=now, updated_at=now)
        session.add(delivery)
    delivery.status = status
    delivery.actual_delivered_at = delivered_at
    delivery.updated_at = now
    return delivery


def _apply_seed(session: Session, data: dict) -> None:
    catalog = data["catalog"]
    year_data = catalog["academic_year"]
    account = _one(session, TeacherAccount, email=SEED_EMAIL)
    if account is None:
        account = TeacherAccount(
            tenant=Tenant(name=catalog["tenant_name"]),
            email=SEED_EMAIL,
            password_hash=hash_password(SEED_PASSWORD),
            role=AccountRole.TEACHER,
            status=AccountStatus.ACTIVE,
        )
        session.add(account)
        session.flush()
    else:
        if account.tenant is None:
            account.tenant = Tenant(name=catalog["tenant_name"])
            session.flush()
        account.tenant.name = catalog["tenant_name"]
        account.password_hash = hash_password(SEED_PASSWORD)
        account.role = AccountRole.TEACHER
        account.status = AccountStatus.ACTIVE

    tenant_id = account.tenant_id
    year = _one(session, AcademicYear, tenant_id=tenant_id, label=year_data["label"])
    if year is None:
        year = AcademicYear(tenant_id=tenant_id, label=year_data["label"])
        session.add(year)
        session.flush()
    year.status = AcademicYearStatus.ACTIVE
    year.starts_on = date.fromisoformat(year_data["starts_on"])
    year.ends_on = date.fromisoformat(year_data["ends_on"])
    year.closed_at = None

    subjects = {}
    for name in catalog["subjects"]:
        subject = _one(session, Subject, tenant_id=tenant_id, name=name)
        if subject is None:
            subject = Subject(tenant_id=tenant_id, name=name, description=f"Asignatura de {name.lower()}.")
            session.add(subject)
            session.flush()
        subject.archived = False
        subjects[name] = subject

    section = _one(session, Section, tenant_id=tenant_id, name=catalog["section"])
    if section is None:
        section = Section(tenant_id=tenant_id, name=catalog["section"])
        session.add(section)
        session.flush()
    section.archived = False
    for subject in subjects.values():
        if session.scalar(select(SubjectSection).where(SubjectSection.tenant_id == tenant_id, SubjectSection.subject_id == subject.id, SubjectSection.section_id == section.id)) is None:
            session.add(SubjectSection(tenant_id=tenant_id, subject_id=subject.id, section_id=section.id))

    students = {}
    for student_data in data["students"]:
        student = _one(session, Student, tenant_id=tenant_id, nie=student_data["nie"])
        if student is None:
            student = Student(tenant_id=tenant_id, nie=student_data["nie"], first_name=student_data["first_name"], last_name=student_data["last_name"])
            session.add(student)
            session.flush()
        student.first_name = student_data["first_name"]
        student.last_name = student_data["last_name"]
        student.archived = False
        membership = _one(session, StudentMembership, tenant_id=tenant_id, student_id=student.id, academic_year_id=year.id)
        if membership is None:
            membership = StudentMembership(tenant_id=tenant_id, student_id=student.id, section_id=section.id, academic_year_id=year.id)
            session.add(membership)
        membership.section_id = section.id
        membership.status = MembershipStatus.ACTIVE
        students[student_data["nie"]] = student

    tasks = {}
    for task_data in data["tasks"]:
        task = _one(session, Task, tenant_id=tenant_id, title=task_data["title"])
        if task is None:
            task = Task(tenant_id=tenant_id, title=task_data["title"], description=task_data["description"], academic_year_id=year.id, subject_id=subjects[task_data["subject"]].id, section_id=section.id, assigned_on=date.fromisoformat(task_data["assigned_on"]), due_on=date.fromisoformat(task_data["due_on"]))
            session.add(task)
            session.flush()
        task.description = task_data["description"]
        task.academic_year_id = year.id
        task.subject_id = subjects[task_data["subject"]].id
        task.section_id = section.id
        task.assigned_on = date.fromisoformat(task_data["assigned_on"])
        task.due_on = date.fromisoformat(task_data["due_on"])
        task.archived = False
        tasks[task_data["title"]] = task

    deliveries = {}
    for delivery_data in data["delivery_states"]:
        delivered_at = delivery_data.get("delivered_at")
        delivery = _get_or_create_delivery(session, tenant_id, tasks[delivery_data["task"]].id, students[delivery_data["student"]].id, DeliveryStatus(delivery_data["status"]), datetime.fromisoformat(delivered_at) if delivered_at else None)
        deliveries[(delivery_data["task"], delivery_data["student"])] = delivery
    session.flush()

    for fixture_name, model, values in (
        ("evidence", Evidence, {"kind": "kind", "url": "url"}),
        ("private_observation", PrivateObservation, {"body": "body"}),
    ):
        fixture = data["fixtures"][fixture_name]
        delivery = deliveries[(fixture["task"], fixture["student"])]
        filters = {"tenant_id": tenant_id, "delivery_id": delivery.id}
        filters.update({column: fixture[source] for column, source in values.items()})
        if _one(session, model, **filters) is None:
            fields = dict(filters)
            fields["created_at"] = datetime.now(UTC)
            if model is PrivateObservation:
                fields["author_teacher_id"] = account.id
            session.add(model(**fields))


def seed(session: Session) -> None:
    """Create or refresh the stable, non-grading development dataset."""
    data = load_seed_data()
    get_settings()
    try:
        _apply_seed(session, data)
        session.commit()
    except Exception:
        session.rollback()
        raise


def main() -> None:
    with SessionLocal() as session:
        seed(session)
    print(f"Seed de desarrollo actualizado para {SEED_EMAIL}.")


if __name__ == "__main__":
    main()
