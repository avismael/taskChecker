from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_initial_migration_creates_schema(tmp_path):
    database = tmp_path / "migration.db"
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database}")

    command.upgrade(config, "head")

    tables = set(inspect(create_engine(f"sqlite:///{database}")).get_table_names())
    assert {"tenants", "teacher_accounts", "audit_events", "deliveries"}.issubset(tables)

    command.downgrade(config, "base")
    assert inspect(create_engine(f"sqlite:///{database}")).get_table_names() == ["alembic_version"]

    command.upgrade(config, "head")
    assert "tasks" in inspect(create_engine(f"sqlite:///{database}")).get_table_names()
