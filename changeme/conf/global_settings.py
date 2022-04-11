from pathlib import Path

from changeme.types.config import Migration

BASE_PATH = Path.cwd().parent.parent
SQL = "sqlite:///db.sqlite"
ASQL = "sqlite+aiosqlite:///db.sqlite"

MIGRATIONS = {
    "auth": Migration(
        models=["changeme.models.user"],
        migrations_module="changeme.db:migrations",
        version_table="changeme"
    )
}
