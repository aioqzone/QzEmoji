from pathlib import Path
from typing import Callable, cast, Optional, Union

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class EmojiOrm(Base):    # type: ignore
    __tablename__ = 'Emoji'

    eid = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.VARCHAR)


class AsyncEnginew:
    @classmethod
    def sqlite3(cls, path: Optional[Path], **kwds):
        if path is None: url = "sqlite+aiosqlite://"
        else: url = "sqlite+aiosqlite:///" + path.as_posix()
        # make dir if parent not exist
        if path: path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_async_engine(url, **kwds)
        return cls(engine)

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def __aenter__(self):
        return self.engine

    async def __aexit__(self, *exc):
        await self.engine.dispose()


class EmojiTable:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.sess = sessionmaker(engine, class_=AsyncSession)

    async def create(self):
        """
        The create function creates a new table in the database.
        It takes no arguments and returns nothing.
        """
        
        async with self.engine.begin() as conn:
            await conn.run_sync(EmojiOrm.metadata.create_all)

    async def query(self, eid: int, default: Union[Callable[[int], str], str] = None) -> str:
        """
        The query function takes an emoji ID and returns the corresponding string.
        If no emoji is found, it will return string identified by `default`.
        
        :param eid: Used to identify the emoji.
        :param default: Used to specify a default value, defaults to return str(eid).
        :return: a string representation of the emoji.
        """

        async with self.sess() as sess:
            stmt = select(EmojiOrm).where(EmojiOrm.eid == eid)
            result = await sess.execute(stmt)
        r: Optional[EmojiOrm] = result.scalar()
        if r: return cast(str, r.text)
        if default is None: return str(eid)
        if callable(default): return default(eid)
        return default

    async def set(self, eid: int, text: str):
        """
        The set function is used to set the text of an emoji.
        It takes three arguments: eid, text, and flush.
        eid is the id of the emoji you want to change.
        text is what you want to set it's current text into.
        
        :param eid: Used to identify the emoji.
        :param text: Used to set the text of an emoji.
        :return: None.
        """
        
        async with self.sess() as sess:
            async with sess.begin():
                result = await sess.execute(select(EmojiOrm).where(EmojiOrm.eid == eid))
                if (prev := result.scalar()):
                    # if exist: update
                    prev.text = text
                else:
                    # not exist: add
                    sess.add(EmojiOrm(eid=eid, text=text))
            await sess.commit()
