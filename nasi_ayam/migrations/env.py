"""Alembic environment configuration."""

import os

from alembic import context
from sqlalchemy import create_engine

config = context.config

raw_database_url = os.environ.get(
    "DATABASE_URL",
    "postgresql://nasi_ayam:nasi_ayam@localhost:5432/nasi_ayam",
)
database_url = raw_database_url.replace("postgresql://", "postgresql+psycopg://", 1)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    engine = create_engine(database_url)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
