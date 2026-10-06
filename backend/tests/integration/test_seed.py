from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.app.persistence.base import Base
from backend.app.persistence.models import (
    AcademicYear,
    Delivery,
    Evidence,
    PrivateObservation,
    Student,
    Subject,
    SubjectSection,
    Task,
    TeacherAccount,
)
from backend.app.persistence.models.delivery import DeliveryStatus
from backend.app.persistence.models.organization import AcademicYearStatus
from backend.app.scripts.seed import DATA_DIR, SEED_EMAIL, load_seed_data, seed


def test_seed_data_is_loaded_relative_to_seed_module(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    data = load_seed_data()

    assert DATA_DIR.name == "seed_data"
    assert data["catalog"]["section"] == "3.º ESO A"
    assert data["students"][0]["nie"] == "SEED-001"
    assert data["tasks"][0]["title"] == "SEED-TASK-01 · Comentario de texto"


def test_seed_data_validation_rejects_missing_sections():
    from backend.app.scripts.seed import SeedDataError, validate_seed_data

    try:
        validate_seed_data({"catalog": {}})
    except SeedDataError as error:
        assert "students" in str(error)
    else:
        raise AssertionError("Expected malformed seed data to be rejected")


def test_seed_creates_representative_development_data_in_isolated_database(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'seed.db'}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed(session)

        assert session.scalar(select(func.count(TeacherAccount.id))) == 1
        assert session.scalar(select(func.count(AcademicYear.id))) == 1
        assert session.scalar(select(AcademicYear.status)) == AcademicYearStatus.ACTIVE
        assert session.scalar(select(func.count(Subject.id))) == 2
        assert session.scalar(select(func.count(SubjectSection.subject_id))) == 2
        assert session.scalar(select(func.count(Student.id))) == 3
        assert session.scalar(select(func.count(Task.id))) == 2
        assert session.scalar(select(func.count(Delivery.id))) == 6
        assert session.scalar(select(func.count(Evidence.id))) == 1
        assert session.scalar(select(func.count(PrivateObservation.id))) == 1
        assert set(session.scalars(select(Delivery.status))) == {
            DeliveryStatus.PENDING,
            DeliveryStatus.DELIVERED,
            DeliveryStatus.LATE,
            DeliveryStatus.NOT_DELIVERED,
            DeliveryStatus.COMPLETED,
        }
        assert session.scalar(select(TeacherAccount.email)) == SEED_EMAIL


def test_seed_is_idempotent_when_run_twice(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'seed.db'}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed(session)
        first_ids = {
            model.__name__: {str(item.id) for item in session.scalars(select(model))}
            for model in (AcademicYear, Student, Task, Delivery, Evidence, PrivateObservation)
        }
        seed(session)

        second_ids = {
            model.__name__: {str(item.id) for item in session.scalars(select(model))}
            for model in (AcademicYear, Student, Task, Delivery, Evidence, PrivateObservation)
        }
        assert second_ids == first_ids
        assert session.scalar(select(func.count(SubjectSection.subject_id))) == 2
