from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.app.services.student_import_service import commit_student_import, parse_student_import


def test_csv_preview_reports_missing_and_duplicate_fields():
    rows = parse_student_import(
        "students.csv",
        b"nie,nombre,apellido\nA1,Ana,Lopez\nA1,,Diaz\n,Bob,Smith\n",
    )
    assert rows[0].errors == ()
    assert "Duplicate NIE in import" in rows[1].errors
    assert "First name is required" in rows[1].errors
    assert "NIE is required" in rows[2].errors


def test_invalid_import_cannot_be_committed():
    rows = parse_student_import("students.csv", b"nie,nombre,apellido\n,,\n")
    with pytest.raises(ValueError, match="validation errors"):
        commit_student_import(Mock(), uuid4(), uuid4(), uuid4(), rows, uuid4())
