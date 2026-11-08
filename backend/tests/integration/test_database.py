import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

pytestmark = pytest.mark.integration


def test_migrations_vector_and_rollback(monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL")
    assert url, "TEST_DATABASE_URL must point to the disposable plantly_test database"
    parsed = make_url(url)
    assert parsed.drivername == "postgresql+psycopg"
    assert parsed.database == "plantly_test", "Refusing to migrate a non-test database"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            revision = connection.scalar(
                text("SELECT version_num FROM alembic_version")
            )
            assert revision == ("0001_vector")
            distance = connection.scalar(
                text("SELECT '[1,2]'::vector <-> '[1,2]'::vector")
            )
            assert distance == 0
            connection.execute(text("CREATE TEMP TABLE rollback_probe (value integer)"))
            connection.commit()
            connection.execute(text("INSERT INTO rollback_probe VALUES (1)"))
            connection.rollback()
            assert connection.scalar(text("SELECT count(*) FROM rollback_probe")) == 0
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        command.check(config)
    finally:
        engine.dispose()
