from dataclasses import dataclass

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import func, select
from sqlalchemy.sql.selectable import Select
from changeme.utils import get_package_dir


@dataclass
class PageCalc:
    limit: int
    offset: int
    next_page: int


@dataclass
class Pagination:
    total: int
    limit: int
    page: int


async def get_total_async(session, Model):
    """Should be made in a context manager"""
    stmt = select(func.count(Model.id))
    _total = await session.execute(stmt)
    total = _total.scalar()

    return total


def get_total(session, Model):
    """Should be made in a context manager"""
    stmt = select(func.count(Model.id))
    _total = session.execute(stmt)
    total = _total.scalar()

    return total


def pagination(s: Select, p: Pagination):

    offset = p.limit * (p.page - 1)
    next_page = p.page + 1
    next_offset = p.limit * p.page
    if next_offset >= p.total:
        next_page = -1
    stmt = s.limit(p.limit).offset(offset)
    return stmt, next_page


def calculate_page(total, limit, page) -> PageCalc:
    offset = limit * (page - 1)
    next_page = page + 1
    next_offset = limit * page
    if next_offset >= total:
        next_page = -1
    return PageCalc(limit=limit, offset=offset, next_page=next_page)


def alembic_ugprade(dburi, to="head"):
    dir_ = get_package_dir("changeme.db")
    alembic_file = f"{dir_}/alembic.ini"

    alembic_cfg = AlembicConfig(alembic_file)
    alembic_cfg.set_main_option("sqlalchemy.url", dburi)
    command.upgrade(alembic_cfg, to)
