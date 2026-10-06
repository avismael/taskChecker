from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.observability.logging import log_event
from backend.app.persistence.repositories.audit import record_audit


def audit(
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
):
    event = record_audit(
        session,
        tenant_id=tenant_id,
        actor_account_id=actor_account_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        previous_values=previous_values,
        new_values=new_values,
        automation_source=automation_source,
        reason=reason,
    )
    log_event(
        "audit_recorded",
        tenant_id=str(tenant_id) if tenant_id else None,
        actor_account_id=str(actor_account_id) if actor_account_id else None,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
    )
    return event
