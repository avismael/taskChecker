from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.persistence.models.audit import AuditEvent


def record_audit(
    session: Session,
    *,
    tenant_id: UUID | None,
    actor_account_id: UUID | None,
    resource_type: str,
    resource_id: str,
    action: str,
    previous_values: dict | None = None,
    new_values: dict | None = None,
    automation_source: str | None = None,
    reason: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        tenant_id=tenant_id,
        actor_account_id=actor_account_id,
        automation_source=automation_source,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        previous_values=previous_values,
        new_values=new_values,
        reason=reason,
    )
    session.add(event)
    return event
