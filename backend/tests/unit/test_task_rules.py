from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.app.services.task_service import create_task


def test_task_rejects_due_date_before_assignment():
    with pytest.raises(ValueError, match="Due date cannot precede assignment"):
        create_task(
            Mock(),
            uuid4(),
            uuid4(),
            uuid4(),
            uuid4(),
            "Task",
            "",
            date(2026, 10, 10),
            date(2026, 10, 1),
        )


def test_task_rejects_foreign_academic_references():
    session = Mock()
    session.scalar.return_value = None

    with pytest.raises(ValueError, match="does not belong to this tenant"):
        create_task(
            session,
            uuid4(),
            uuid4(),
            uuid4(),
            uuid4(),
            "Task",
            "",
            date(2026, 10, 1),
            date(2026, 10, 10),
        )
