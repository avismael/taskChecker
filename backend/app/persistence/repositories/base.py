from typing import Any
from uuid import UUID

from sqlalchemy import Select


def tenant_filter(statement: Select[Any], model: Any, tenant_id: UUID) -> Select[Any]:
    """Require callers to make tenant ownership explicit in every query."""
    return statement.where(model.tenant_id == tenant_id)


def normalize_email(email: str) -> str:
    return email.strip().casefold()
