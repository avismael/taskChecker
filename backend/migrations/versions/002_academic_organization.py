"""Create academic years, organization records, and memberships."""

from alembic import op

from backend.app.persistence import models  # noqa: F401
from backend.app.persistence.base import Base

revision = "002_academic_organization"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in (
        "academic_years",
        "subjects",
        "sections",
        "subject_sections",
        "students",
        "student_memberships",
    ):
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in (
        "student_memberships",
        "students",
        "subject_sections",
        "sections",
        "subjects",
        "academic_years",
    ):
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=True)
