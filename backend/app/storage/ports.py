from pathlib import Path
from typing import Protocol
from uuid import UUID

ALLOWED_EVIDENCE_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".webp"}
OPENXML_EXTENSIONS = {".docx", ".xlsx", ".pptx"}


class EvidenceStorage(Protocol):
    def save(self, tenant_id: UUID, evidence_id: UUID, filename: str, content: bytes) -> str: ...


def validate_evidence(filename: str, content_type: str, content: bytes | None = None) -> None:
    suffix = Path(filename).suffix.casefold()
    if suffix == ".zip" or suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported evidence type; ZIP archives are not allowed.")
    if content_type == "application/zip":
        raise ValueError("Unsupported evidence type; ZIP archives are not allowed.")
    if content and content.startswith(b"PK") and suffix not in OPENXML_EXTENSIONS:
        raise ValueError("Unsupported evidence type; ZIP archives are not allowed.")
