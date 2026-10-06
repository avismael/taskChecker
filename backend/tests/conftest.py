import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture
def client():
    from backend.app.api.security import reset_rate_limits

    reset_rate_limits()
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def unique_email():
    return f"teacher-{uuid.uuid4().hex}@example.com"


@pytest.fixture
def session():
    from backend.app.persistence.session import SessionLocal

    with SessionLocal() as value:
        yield value


@pytest.fixture
def tenant_id(unique_email, session):
    from backend.app.services.auth_service import register_teacher

    account = register_teacher(session, unique_email, "safe-password")
    return account.tenant_id
