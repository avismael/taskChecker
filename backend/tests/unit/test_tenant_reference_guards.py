from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.app.services.organization_service import link_subject_section
from backend.app.services.student_service import create_student
from backend.app.services.task_service import create_task


def test_link_rejects_foreign_references():
    session = Mock()
    session.scalar.return_value = None
    with pytest.raises(ValueError, match="does not belong"):
        link_subject_section(session, uuid4(), uuid4(), uuid4())


def test_student_rejects_foreign_references():
    session = Mock()
    session.scalar.return_value = None
    with pytest.raises(ValueError, match="does not belong"):
        create_student(session, uuid4(), uuid4(), uuid4(), "A1", "First", "Last")


def test_task_rejects_foreign_references():
    session = Mock()
    session.scalar.return_value = None
    with pytest.raises(ValueError, match="does not belong"):
        create_task(session, uuid4(), uuid4(), uuid4(), uuid4(), "Task", "", date(2026, 1, 1), date(2026, 1, 2))
