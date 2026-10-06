from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import CurrentActor, require_teacher
from backend.app.api.security import read_upload
from backend.app.config import get_settings
from backend.app.persistence.models.delivery import DeliveryStatus
from backend.app.persistence.session import get_db
from backend.app.services.delivery_service import (
    add_file_evidence,
    add_link_evidence,
    add_observation,
    delivery_history,
    set_delivery_status,
)

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


class DeliveryPayload(BaseModel):
    status: DeliveryStatus
    actual_delivered_at: datetime | None = None


class ObservationPayload(BaseModel):
    body: str


class LinkPayload(BaseModel):
    url: str


@router.patch("/{delivery_id}")
def update_delivery(
    delivery_id: UUID,
    payload: DeliveryPayload,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    item = set_delivery_status(
        session, actor.tenant_id, delivery_id, payload.status, payload.actual_delivered_at, actor.account_id
    )
    return {
        "id": str(item.id),
        "status": item.status.value,
        "actual_delivered_at": str(item.actual_delivered_at) if item.actual_delivered_at else None,
    }


@router.post("/{delivery_id}/observations")
def observation(
    delivery_id: UUID,
    payload: ObservationPayload,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    item = add_observation(session, actor.tenant_id, delivery_id, actor.account_id, payload.body)
    return {"id": str(item.id), "body": item.body}


@router.post("/{delivery_id}/evidence/link")
def evidence_link(
    delivery_id: UUID,
    payload: LinkPayload,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    item = add_link_evidence(session, actor.tenant_id, delivery_id, actor.account_id, payload.url)
    return {"id": str(item.id), "kind": item.kind, "url": item.url}


@router.post("/{delivery_id}/evidence")
async def evidence_file(
    delivery_id: UUID,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    item = add_file_evidence(
        session,
        actor.tenant_id,
        delivery_id,
        actor.account_id,
        file.filename or "evidence",
        file.content_type or "application/octet-stream",
        await read_upload(file, get_settings().max_upload_bytes),
    )
    return {"id": str(item.id), "kind": item.kind, "storage_ref": item.storage_ref}


@router.get("/{delivery_id}/history")
def history(
    delivery_id: UUID,
    actor: Annotated[CurrentActor, Depends(require_teacher)],
    session: Annotated[Session, Depends(get_db)],
):
    return {"delivery_id": str(delivery_id), "events": delivery_history(session, actor.tenant_id, delivery_id)}
