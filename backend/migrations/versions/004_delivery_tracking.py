"""Create delivery, evidence, and private observation records."""

from alembic import op

from backend.app.persistence import models  # noqa: F401
from backend.app.persistence.base import Base

revision = "004_delivery_tracking"
down_revision = "003_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in ("deliveries", "evidence", "private_observations"):
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in ("private_observations", "evidence", "deliveries"):
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=True)
