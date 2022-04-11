import importlib
from typing import List

from alembic import command
from alembic.config import Config as AlembicConfig
from changeme import defaults
from changeme.types.config import Migration
from changeme.utils import get_package_dir


def alembic_config(dburi: str,
                   version_table: str,
                   models_name: List[str],
                   migrations_module=defaults.MIGRATIONS_PKG) -> AlembicConfig:
    dir_ = get_package_dir(defaults.MIGRATIONS_PKG)
    alembic_file = f"{dir_}/alembic.ini"
    models = [importlib.import_module(mod) for mod in models_name]

    alembic_cfg = AlembicConfig(alembic_file)
    alembic_cfg.set_main_option("script_locations", migrations_module)
    alembic_cfg.set_main_option("version_table", version_table)
    alembic_cfg.set_main_option("sqlalchemy.url", dburi)
    return alembic_cfg


def alembic_ugprade(dburi: str,
                    migration: Migration,
                    to="head"):

    cfg = alembic_config(
        dburi,
        migration.version_table,
        migration.models,
        migrations_module=migration.migrations_module)
    command.upgrade(cfg, to)


def alembic_revision(dburi: str,
                     rev_id: str,
                     message: str,
                     migration: Migration,
                     autogenerate=True):
    cfg = alembic_config(dburi, migration.version_table, migration.models,
                         migrations_module=migration.migrations_module)

    command.revision(
        cfg,
        message=message,
        rev_id=rev_id,
        autogenerate=autogenerate)
