from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.observability.logging import log_event
from backend.app.persistence.models.audit import AuditEvent
from backend.app.persistence.models.delivery import (
    Delivery,
    DeliveryStatus,
    Evidence,
    PrivateObservation,
)
from backend.app.persistence.models.task import Task
from backend.app.services.audit_service import audit
from backend.app.storage.local import LocalEvidenceStorage
from backend.app.storage.ports import validate_evidence


def _tenant_delivery(session: Session, tenant_id: UUID, delivery_id: UUID) -> Delivery:
    delivery = session.scalar(
        select(Delivery).where(Delivery.id == delivery_id, Delivery.tenant_id == tenant_id)
    )
    if delivery is None:
        raise ValueError("Delivery not found.")
    return delivery


def set_delivery_status(
    session: Session,
    tenant_id: UUID,
    delivery_id: UUID,
    status: DeliveryStatus,
    actual_delivered_at: datetime | None,
    actor_id: UUID,
) -> Delivery:
    delivery = session.scalar(
        select(Delivery).where(Delivery.id == delivery_id, Delivery.tenant_id == tenant_id)
    )
    if delivery is None:
        raise ValueError("Delivery not found.")
    task = session.get(Task, delivery.task_id)
    if actual_delivered_at and actual_delivered_at.date() < task.assigned_on:
        raise ValueError("Delivery date cannot precede assignment date.")
    try:
        previous = delivery.status.value
        delivery.status = status
        delivery.actual_delivered_at = actual_delivered_at
        delivery.updated_at = datetime.now(UTC)
        audit(
            session,
            tenant_id=tenant_id,
            actor_account_id=actor_id,
            resource_type="delivery",
            resource_id=str(delivery.id),
            action="status_changed",
            previous_values={"status": previous},
            new_values={"status": status.value, "actual_delivered_at": str(actual_delivered_at)},
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(delivery)
    return delivery


def apply_due_date_transitions(session: Session, now: date) -> int:
    rows = session.execute(
        select(Delivery, Task)
        .join(Task, Task.id == Delivery.task_id)
        .where(Delivery.status == DeliveryStatus.PENDING, Task.due_on < now)
    ).all()
    count = 0
    for delivery, task in rows:
        delivery.status = DeliveryStatus.NOT_DELIVERED
        delivery.updated_at = datetime.now(UTC)
        audit(
            session,
            tenant_id=delivery.tenant_id,
            actor_account_id=None,
            resource_type="delivery",
            resource_id=str(delivery.id),
            action="status_changed",
            previous_values={"status": DeliveryStatus.PENDING.value},
            new_values={"status": DeliveryStatus.NOT_DELIVERED.value},
            automation_source="due_date_worker",
        )
        count += 1
    session.commit()
    return count


def add_observation(session: Session, tenant_id: UUID, delivery_id: UUID, actor_id: UUID, body: str):
    if not body.strip():
        raise ValueError("Observation text is required.")
    _tenant_delivery(session, tenant_id, delivery_id)
    item = PrivateObservation(
        tenant_id=tenant_id,
        delivery_id=delivery_id,
        author_teacher_id=actor_id,
        body=body.strip(),
        created_at=datetime.now(UTC),
    )
    session.add(item)
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="private_observation",
        resource_id=str(item.id),
        action="created",
        new_values={"delivery_id": str(delivery_id)},
    )
    session.commit()
    log_event("observation_created", tenant_id=str(tenant_id), delivery_id=str(delivery_id))
    return item


def add_link_evidence(session: Session, tenant_id: UUID, delivery_id: UUID, actor_id: UUID, url: str):
    _tenant_delivery(session, tenant_id, delivery_id)
    item = Evidence(
        tenant_id=tenant_id,
        delivery_id=delivery_id,
        kind="link",
        url=url,
        created_at=datetime.now(UTC),
    )
    session.add(item)
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="evidence",
        resource_id=str(item.id),
        action="created",
        new_values={"kind": "link", "delivery_id": str(delivery_id)},
    )
    session.commit()
    log_event("evidence_linked", tenant_id=str(tenant_id), delivery_id=str(delivery_id))
    return item


def add_file_evidence(
    session: Session,
    tenant_id: UUID,
    delivery_id: UUID,
    actor_id: UUID,
    filename: str,
    content_type: str,
    content: bytes,
):
    _tenant_delivery(session, tenant_id, delivery_id)
    validate_evidence(filename, content_type, content)
    suffix = filename.casefold()
    kind = "image" if content_type.startswith("image/") else "pdf" if suffix.endswith(".pdf") else "office_document"
    item = Evidence(
        tenant_id=tenant_id,
        delivery_id=delivery_id,
        kind=kind,
        original_name=filename,
        content_type=content_type,
        size_bytes=len(content),
        created_at=datetime.now(UTC),
    )
    session.add(item)
    session.flush()
    item.storage_ref = LocalEvidenceStorage(get_settings().storage_root).save(
        tenant_id, item.id, filename, content
    )
    audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_id,
        resource_type="evidence",
        resource_id=str(item.id),
        action="created",
        new_values={"kind": item.kind, "original_name": filename, "delivery_id": str(delivery_id)},
    )
    session.commit()
    log_event("evidence_uploaded", tenant_id=str(tenant_id), delivery_id=str(delivery_id), size_bytes=len(content))
    return item


def delivery_history(session: Session, tenant_id: UUID, delivery_id: UUID) -> list[dict]:
    _tenant_delivery(session, tenant_id, delivery_id)
    events = session.scalars(
        select(AuditEvent)
        .where(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.resource_type.in_(["delivery", "evidence", "private_observation"]),
        )
        .order_by(AuditEvent.occurred_at.desc())
    ).all()
    events = [
        event
        for event in events
        if event.resource_id == str(delivery_id)
        or (event.new_values and event.new_values.get("delivery_id") == str(delivery_id))
    ]
    return [
        {
            "action": event.action,
            "resource_type": event.resource_type,
            "occurred_at": event.occurred_at.isoformat(),
            "previous_values": event.previous_values,
            "new_values": event.new_values,
            "automation_source": event.automation_source,
        }
        for event in events
    ]
