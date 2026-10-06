"""Create tasks and delivery rosters."""

from alembic import op

from backend.app.persistence import models  # noqa: F401
from backend.app.persistence.base import Base

revision = "003_tasks"
down_revision = "002_academic_organization"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.tables["tasks"].create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    Base.metadata.tables["tasks"].drop(bind=op.get_bind(), checkfirst=True)
