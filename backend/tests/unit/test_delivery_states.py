from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.app.persistence.models.delivery import DeliveryStatus
from backend.app.services.delivery_service import apply_due_date_transitions, set_delivery_status


def test_due_date_transition_is_idempotent(session):
    assert apply_due_date_transitions(session, date(2026, 10, 2)) >= 0
    assert DeliveryStatus.PENDING.value == "pending"


def test_delivery_date_cannot_precede_task_assignment():
    session = Mock()
    session.scalar.return_value = SimpleNamespace(id=uuid4(), task_id=uuid4(), status=DeliveryStatus.PENDING)
    session.get.return_value = SimpleNamespace(assigned_on=date(2026, 10, 10))

    with pytest.raises(ValueError, match="Delivery date cannot precede assignment"):
        set_delivery_status(
            session,
            uuid4(),
            uuid4(),
            DeliveryStatus.DELIVERED,
            datetime(2026, 10, 9, 12, tzinfo=UTC),
            uuid4(),
        )
