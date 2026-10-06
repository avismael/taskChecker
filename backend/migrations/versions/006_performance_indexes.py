"""Indexes for roster and report access paths."""

from alembic import op

revision = "006_performance_indexes"
down_revision = "005_follow_up_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_task_deliveries_task_status", "deliveries", ["task_id", "status"])
    op.create_index("ix_memberships_year_section", "student_memberships", ["academic_year_id", "section_id"])


def downgrade() -> None:
    op.drop_index("ix_memberships_year_section", table_name="student_memberships")
    op.drop_index("ix_task_deliveries_task_status", table_name="deliveries")
