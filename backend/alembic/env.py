import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Add application root to Python module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Import application configuration and database base class
from app.core.config import settings
from app.db.session import Base
import app.db.models  # Imports all models so Alembic detects their tables

# Alembic Config object providing access to alembic.ini values
config = context.config

# Dynamically set database URL from environment settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Setup Python logging if config file exists
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate migration support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode without an active DB engine connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode by connecting directly to the PostgreSQL database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()