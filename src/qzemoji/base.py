"""sqlalchemy infrastructure serving this package (and other sqlalchemy applications).
"""

from pathlib import Path
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker as sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase


class AsyncEngineFactory:
    @classmethod
    def sqlite3(cls, path: Optional[Path], **kwds):
        if path is None:
            url = "sqlite+aiosqlite://"
        else:
            url = "sqlite+aiosqlite:///" + path.as_posix()
        # make dir if parent not exist
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_async_engine(url, **kwds)
        return cls(engine)

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def __aenter__(self):
        return self.engine

    async def __aexit__(self, *exc):
        await self.engine.dispose()


class AsyncSessionProvider:
    """AsyncSessionProvider holds the AsyncEngine and provide an interface to the sessionmaker.
    It also provides some common methods.
    """

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self._sess = sessionmaker(engine)

    @property
    def sess(self):
        self.__ensure_async_mutex()
        return self._sess

    def __ensure_async_mutex(self):
        """A temp fix to self.engine.pool.dispatch.connect._exec_once_mutex blocked"""
        from _thread import LockType

        try:
            if isinstance(self.engine.pool.dispatch.connect._exec_once_mutex, LockType):
                self.engine.pool.dispatch.connect._set_asyncio()
        except AttributeError:
            return

    async def _create(
        self, Base: Type[DeclarativeBase], conn: Optional[AsyncConnection] = None
    ) -> None:
        """
        Create all tables derived from `Base`.

        :param Base: the declarative base
        :param conn: use this connection, otherwise we will create one and close it on return.
        """
        if conn is None:
            async with self.engine.begin() as conn:
                return await self._create(Base, conn=conn)

        await conn.run_sync(Base.metadata.create_all)
