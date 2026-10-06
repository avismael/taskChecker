from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from backend.app.observability.logging import log_event
from backend.app.services.delivery_service import apply_due_date_transitions


def run_due_date_worker(session: Session, today: date | None = None) -> int:
    """Transition overdue pending deliveries and return the mutation count."""
    count = apply_due_date_transitions(session, today or datetime.now(UTC).date())
    log_event("due_date_worker_completed", transitioned=count)
    return count
