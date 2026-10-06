from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import CurrentActor, require_admin
from backend.app.persistence.models.account import (
    AccountRole,
    AccountStatus,
    TeacherAccount,
    Tenant,
)
from backend.app.persistence.repositories.audit import record_audit
from backend.app.persistence.session import get_db
from backend.app.services.auth_service import hash_password

router = APIRouter(prefix="/admin/teachers", tags=["admin"])


class TeacherCreate(BaseModel):
    email: EmailStr
    password: str


class TeacherUpdate(BaseModel):
    status: AccountStatus


@router.post("", status_code=status.HTTP_201_CREATED)
def create_teacher(
    payload: TeacherCreate,
    _: object = Depends(require_admin),
    session: Annotated[Session, Depends(get_db)] = None,
):
    email = str(payload.email).casefold()
    if session.scalar(select(TeacherAccount).where(TeacherAccount.email == email)):
        raise HTTPException(status_code=409, detail="Account already exists")
    tenant = Tenant(name=email)
    account = TeacherAccount(
        tenant=tenant,
        email=email,
        password_hash=hash_password(payload.password),
        role=AccountRole.TEACHER,
        status=AccountStatus.ACTIVE,
    )
    session.add(account)
    session.flush()
    record_audit(
        session,
        tenant_id=tenant.id,
        actor_account_id=None,
        resource_type="teacher_account",
        resource_id=str(account.id),
        action="created_by_admin",
        new_values={"email": email},
    )
    session.commit()
    return {"id": str(account.id), "email": email, "status": account.status.value}


@router.patch("/{teacher_id}")
def update_teacher(
    teacher_id: UUID,
    payload: TeacherUpdate,
    actor: Annotated[CurrentActor, Depends(require_admin)],
    session: Annotated[Session, Depends(get_db)] = None,
):
    account = session.scalar(
        select(TeacherAccount).where(
            TeacherAccount.id == teacher_id,
            TeacherAccount.role == AccountRole.TEACHER,
        )
    )
    if account is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    account.status = payload.status
    record_audit(
        session,
        tenant_id=account.tenant_id,
        actor_account_id=actor.account_id,
        resource_type="teacher_account",
        resource_id=str(account.id),
        action="status_changed",
        new_values={"status": account.status.value},
    )
    session.commit()
    return {"id": str(account.id), "email": account.email, "status": account.status.value}
