import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.persistence.models.account import (
    AccountRole,
    AccountStatus,
    TeacherAccount,
    Tenant,
)
from backend.app.persistence.repositories.audit import record_audit
from backend.app.persistence.repositories.base import normalize_email

password_hasher = PasswordHasher()
_recovery_tokens: dict[str, tuple[str, datetime]] = {}


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def register_teacher(session: Session, email: str, password: str) -> TeacherAccount:
    normalized_email = normalize_email(email)
    if session.scalar(select(TeacherAccount).where(TeacherAccount.email == normalized_email)):
        raise ValueError("An account with this email already exists.")
    tenant = Tenant(id=uuid4(), name=normalized_email)
    account = TeacherAccount(
        tenant=tenant,
        email=normalized_email,
        password_hash=hash_password(password),
        role=AccountRole.TEACHER,
        status=AccountStatus.ACTIVE,
    )
    session.add(account)
    session.flush()
    record_audit(
        session,
        tenant_id=tenant.id,
        actor_account_id=account.id,
        resource_type="teacher_account",
        resource_id=str(account.id),
        action="registered",
        new_values={"email": normalized_email, "status": account.status.value},
    )
    session.commit()
    session.refresh(account)
    return account


def authenticate(session: Session, email: str, password: str) -> TeacherAccount | None:
    account = session.scalar(
        select(TeacherAccount).where(TeacherAccount.email == normalize_email(email))
    )
    if account is None or account.status != AccountStatus.ACTIVE:
        return None
    return account if verify_password(password, account.password_hash) else None


def request_recovery(session: Session, email: str) -> str | None:
    account = session.scalar(
        select(TeacherAccount).where(TeacherAccount.email == normalize_email(email))
    )
    if account is None:
        return None
    token = secrets.token_urlsafe(32)
    _recovery_tokens[token] = (str(account.id), datetime.now(UTC) + timedelta(minutes=30))
    return token


def change_password(session: Session, account: TeacherAccount, password: str) -> None:
    account.password_hash = hash_password(password)
    record_audit(
        session,
        tenant_id=account.tenant_id,
        actor_account_id=account.id,
        resource_type="teacher_account",
        resource_id=str(account.id),
        action="password_changed",
    )
    session.commit()
