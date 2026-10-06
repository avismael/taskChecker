from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.app.services.delivery_service import add_observation
from backend.app.storage.ports import validate_evidence


def test_zip_evidence_is_rejected():
    with pytest.raises(ValueError, match="ZIP"):
        validate_evidence("work.zip", "application/zip")


def test_zip_signature_is_rejected_even_with_pdf_metadata():
    with pytest.raises(ValueError, match="ZIP"):
        validate_evidence("renamed.pdf", "application/pdf", b"PK\x03\x04")


def test_openxml_evidence_may_use_zip_container():
    validate_evidence(
        "worksheet.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        b"PK\x03\x04",
    )


def test_pdf_image_and_office_evidence_types_are_allowed():
    validate_evidence("worksheet.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    validate_evidence("photo.png", "image/png")
    validate_evidence("report.pdf", "application/pdf")


def test_blank_private_observation_is_rejected_before_persistence():
    with pytest.raises(ValueError, match="Observation text is required"):
        add_observation(Mock(), uuid4(), uuid4(), uuid4(), "   ")
