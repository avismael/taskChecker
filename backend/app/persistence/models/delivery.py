from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.persistence.base import Base


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    NOT_DELIVERED = "not_delivered"
    LATE = "late"
    COMPLETED = "completed"


class Delivery(Base):
    __tablename__ = "deliveries"
    __table_args__ = (UniqueConstraint("task_id", "student_id", name="uq_delivery_task_student"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("students.id"), index=True)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False
    )
    actual_delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    delivery_id: Mapped[UUID] = mapped_column(ForeignKey("deliveries.id"), index=True)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_ref: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PrivateObservation(Base):
    __tablename__ = "private_observations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    delivery_id: Mapped[UUID] = mapped_column(ForeignKey("deliveries.id"), index=True)
    author_teacher_id: Mapped[UUID] = mapped_column(ForeignKey("teacher_accounts.id"))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
