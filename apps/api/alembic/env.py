"""
Alembic migration environment.

DATABASE_URL is read from the .env file via pydantic-settings — no need to
hardcode credentials here or in alembic.ini.

All SQLAlchemy models must be imported (directly or transitively) before
autogenerate runs so that Base.metadata is fully populated.
models/__init__.py imports every model, so a single import here is enough.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure apps/api/ is on sys.path so local imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import get_settings

# Import all models via __init__.py — populates Base.metadata
from models import Base  # noqa: F401 (side-effect import)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return get_settings().DATABASE_URL


def run_migrations_offline() -> None:
    """
    Run migrations without a live DB connection.
    Useful for generating SQL scripts to review before applying.
    """
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # no pooling during migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # detect column type changes
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
