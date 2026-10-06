from uuid import UUID

from fastapi import HTTPException, status


def require_tenant(tenant_id: UUID | None) -> UUID:
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "tenant_required", "message": "A teacher tenant is required."},
        )
    return tenant_id
