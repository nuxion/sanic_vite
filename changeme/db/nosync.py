import logging
from contextlib import asynccontextmanager

from changeme.db.common import Base
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.selectable import Select


class AsyncSQL:
    """
    As example checks:
    https://docs.sqlalchemy.org/en/14/_modules/examples/asyncio/async_orm.html
    """

    Meta = MetaData()

    def __init__(self, uri, echo=False):
        self._session = None
        self._engine = None
        self._uri = uri
        self._echo = echo
        # self.meta = MetaData()

    def __getattr__(self, name):
        return getattr(self._session, name)

    @property
    def engine(self):
        return self._engine

    async def init(self, pool_size=20, max_overflow=0):
        if "sqlite" in self._uri.split("://", maxsplit=1)[0]:
            self._engine = create_async_engine(self._uri)
        else:
            self._engine = create_async_engine(
                self._uri,
                echo=self._echo,
                pool_size=pool_size,
                max_overflow=max_overflow,
            )
        self.Meta.bind = self._engine

    def sessionmaker(self, expire_on_commit=False):
        """
        expire_on_commit=False will prevent attributes from being expired
        after commit
        """
        return sessionmaker(
            self._engine, expire_on_commit=expire_on_commit, class_=AsyncSession
        )()

    async def create_all(self):
        """ Create tables  """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        """ drop tables """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
