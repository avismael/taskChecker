from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.persistence.base import Base, TimestampMixin


class AcademicYearStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"


class MembershipStatus(StrEnum):
    ACTIVE = "active"
    ENDED = "ended"


class AcademicYear(TimestampMixin, Base):
    __tablename__ = "academic_years"
    __table_args__ = (UniqueConstraint("tenant_id", "label", name="uq_year_tenant_label"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[AcademicYearStatus] = mapped_column(
        Enum(AcademicYearStatus), default=AcademicYearStatus.ACTIVE, nullable=False
    )
    starts_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_at: Mapped[date | None] = mapped_column(Date, nullable=True)


class Subject(TimestampMixin, Base):
    __tablename__ = "subjects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Section(TimestampMixin, Base):
    __tablename__ = "sections"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SubjectSection(Base):
    __tablename__ = "subject_sections"
    __table_args__ = (UniqueConstraint("subject_id", "section_id", name="uq_subject_section"),)

    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id"), primary_key=True)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id"), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)


class Student(TimestampMixin, Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("tenant_id", "nie", name="uq_student_tenant_nie"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    nie: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class StudentMembership(TimestampMixin, Base):
    __tablename__ = "student_memberships"
    __table_args__ = (
        UniqueConstraint("student_id", "academic_year_id", name="uq_student_year_membership"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("students.id"), index=True)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id"), index=True)
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id"), index=True)
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus), default=MembershipStatus.ACTIVE, nullable=False
    )
