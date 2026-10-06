from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.persistence.models.account import AccountRole, AccountStatus, TeacherAccount
from backend.app.persistence.session import get_db


@dataclass(frozen=True)
class CurrentActor:
    account_id: UUID
    role: AccountRole
    tenant_id: UUID | None


def get_current_actor(request: Request, session: Session = Depends(get_db)) -> CurrentActor:
    account_id = request.session.get("account_id")
    if not account_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    account = session.scalar(select(TeacherAccount).where(TeacherAccount.id == UUID(account_id)))
    if account is None or account.status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return CurrentActor(account.id, account.role, account.tenant_id)


def require_teacher(actor: CurrentActor = Depends(get_current_actor)) -> CurrentActor:
    if actor.role != AccountRole.TEACHER or actor.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher access required")
    return actor


def require_admin(actor: CurrentActor = Depends(get_current_actor)) -> CurrentActor:
    if actor.role != AccountRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return actor
