from secrets import token_urlsafe
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.api.dependencies.auth import get_current_actor
from backend.app.api.security import enforce_rate_limit
from backend.app.config import get_settings
from backend.app.persistence.models.account import TeacherAccount
from backend.app.persistence.session import get_db
from backend.app.services.auth_service import (
    authenticate,
    change_password,
    register_teacher,
    request_recovery,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    email: EmailStr
    password: str


class RecoveryRequest(BaseModel):
    email: EmailStr


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: Credentials, request: Request, session: Annotated[Session, Depends(get_db)]):
    enforce_rate_limit(request, "register", get_settings().auth_rate_limit)
    account = register_teacher(session, str(payload.email), payload.password)
    return {"id": str(account.id), "email": account.email, "status": account.status.value}


@router.post("/login")
def login(payload: Credentials, request: Request, session: Annotated[Session, Depends(get_db)]):
    enforce_rate_limit(request, "login", get_settings().auth_rate_limit)
    account = authenticate(session, str(payload.email), payload.password)
    if account is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["account_id"] = str(account.id)
    request.session["account_email"] = account.email
    request.session["account_role"] = account.role.value
    request.session["csrf_token"] = token_urlsafe(32)
    return {"id": str(account.id), "role": account.role.value, "tenant_id": str(account.tenant_id)}


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"logged_out": True}


@router.post("/recovery")
def recovery(payload: RecoveryRequest, request: Request, session: Annotated[Session, Depends(get_db)]):
    enforce_rate_limit(request, "recovery", get_settings().auth_rate_limit)
    token = request_recovery(session, str(payload.email))
    return {"accepted": True, "token": token} if token else {"accepted": True}


@router.post("/password")
def password(
    payload: Credentials,
    actor=Depends(get_current_actor),
    session: Session = Depends(get_db),
):
    account = session.get(TeacherAccount, actor.account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    change_password(session, account, payload.password)
    return {"changed": True}
