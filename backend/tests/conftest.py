"""PostgreSQL test bootstrap. Collection never connects to the database."""

import os
from pathlib import Path
import secrets
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session


def _configure_test_database():
    raw_url = os.environ.get("TEST_DATABASE_URL")
    if not raw_url:
        raise pytest.UsageError("TEST_DATABASE_URL must be explicitly set.")
    try:
        url = make_url(raw_url)
        allowed = (
            url.drivername in ("postgresql", "postgresql+psycopg2")
            and url.host == "db-test"
            and url.port == 5432
            and url.database == "med_test"
            and url.username == "med_test"
            and bool(url.password)
            and not url.query
        )
    except (ArgumentError, ValueError):
        allowed = False
    if not allowed:
        raise pytest.UsageError(
            "TEST_DATABASE_URL must target db-test:5432/med_test as med_test "
            "using PostgreSQL/psycopg2, with a password and no query parameters."
        )
    if "app.core.config" in sys.modules or "app.db.session" in sys.modules:
        raise pytest.UsageError("Test database configuration must precede application imports.")

    # Alembic env.py and application models read these settings at import time.
    os.environ["DATABASE_URL"] = raw_url
    os.environ["SECRET_KEY"] = secrets.token_urlsafe(32)
    return url


TEST_DATABASE_URL = _configure_test_database()


@pytest.fixture(scope="session")
def migrated_engine():
    """Apply existing migrations only when a database test requests this fixture."""
    from alembic import command
    from alembic.config import Config
    from alembic.migration import MigrationContext
    from alembic.script import ScriptDirectory
    from app.core.config import settings

    if make_url(settings.DATABASE_URL) != TEST_DATABASE_URL:
        raise pytest.UsageError("Application database URL differs from the validated test URL.")

    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    command.upgrade(config, "head")

    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            current = MigrationContext.configure(connection).get_current_heads()
            expected = ScriptDirectory.from_config(config).get_heads()
            if set(current) != set(expected):
                raise pytest.UsageError("Test database is not at the Alembic migration head.")
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(migrated_engine):
    """Roll back each test's changes, including calls to Session.commit()."""
    with migrated_engine.connect() as connection:
        transaction = connection.begin()
        try:
            with Session(
                bind=connection,
                join_transaction_mode="create_savepoint",
            ) as session:
                yield session
        finally:
            transaction.rollback()
