"""Indexes used by follow-up filters and dashboards."""

from alembic import op

revision = "005_follow_up_indexes"
down_revision = "004_delivery_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_deliveries_tenant_status", "deliveries", ["tenant_id", "status"])
    op.create_index("ix_tasks_tenant_due_on", "tasks", ["tenant_id", "due_on"])
    op.create_index("ix_students_tenant_nie", "students", ["tenant_id", "nie"])


def downgrade() -> None:
    op.drop_index("ix_students_tenant_nie", table_name="students")
    op.drop_index("ix_tasks_tenant_due_on", table_name="tasks")
    op.drop_index("ix_deliveries_tenant_status", table_name="deliveries")
