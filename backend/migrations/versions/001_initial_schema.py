"""Create the initial TaskChecker schema.

The declarative metadata is the source of truth for this first migration. Future
migrations should make explicit additive changes rather than calling create_all.
"""

from alembic import op

from backend.app.persistence import models  # noqa: F401
from backend.app.persistence.base import Base

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in ("tenants", "teacher_accounts", "audit_events"):
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in ("audit_events", "teacher_accounts", "tenants"):
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=True)
