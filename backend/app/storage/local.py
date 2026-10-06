from pathlib import Path
from uuid import UUID

from backend.app.storage.ports import EvidenceStorage


class LocalEvidenceStorage(EvidenceStorage):
    def __init__(self, root: str):
        self.root = Path(root)

    def save(self, tenant_id: UUID, evidence_id: UUID, filename: str, content: bytes) -> str:
        destination = self.root / str(tenant_id) / str(evidence_id)
        destination.mkdir(parents=True, exist_ok=True)
        path = destination / Path(filename).name
        path.write_bytes(content)
        return str(path)
