from __future__ import annotations

import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make project root importable when Alembic is run from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / '.env')
except Exception:
    # Alembic should still work in environments where python-dotenv is absent.
    pass

from src.ragforge.stores.postgres.models import Base  # noqa: E402
from src.ragforge.stores.postgres.session import (  # noqa: E402
    PostgresConnectionSettings,
    build_postgres_sync_url,
    escape_alembic_url,
)

# Import model modules so Base.metadata is fully populated for autogenerate.
from src.ragforge.stores.postgres.models import (  # noqa: E402,F401
    AssetTable,
    DataChunkTable,
    ProjectTable,
    VectorRecordTable,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_connection() -> PostgresConnectionSettings:
    return PostgresConnectionSettings(
        username=os.getenv('POSTGRES_USER', 'ragforge'),
        password=os.getenv('POSTGRES_PASSWORD', 'ragforge_password_change_me'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', '5433')),
        database=os.getenv('POSTGRES_DB', 'ragforge'),
    )


def _set_sqlalchemy_url() -> None:
    url = build_postgres_sync_url(_get_connection())
    config.set_main_option('sqlalchemy.url', escape_alembic_url(url))


def run_migrations_offline() -> None:
    _set_sqlalchemy_url()
    url = config.get_main_option('sqlalchemy.url')

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    _set_sqlalchemy_url()
    configuration = config.get_section(config.config_ini_section, {})
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
