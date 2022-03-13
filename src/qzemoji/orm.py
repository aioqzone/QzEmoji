from pathlib import Path
from typing import Callable, Optional, Union, cast

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class EmojiOrm(Base):  # type: ignore
    __tablename__ = "Emoji"

    eid = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.VARCHAR)


class MyEmoji(Base):  # type: ignore
    __tablename__ = "MyEmoji"

    eid = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.VARCHAR)


class AsyncEnginew:
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


class EmojiTable:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.sess = sessionmaker(engine, class_=AsyncSession)

    async def create(self):
        """
        The create function creates `Emoji` and `MyEmoji` table in the database.
        It takes no arguments and returns nothing.
        """

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)  # type: ignore

    async def is_corrupt(self) -> bool:
        def test2(conn):
            insp = sa.inspect(conn)
            return insp.has_table("Emoji") and insp.has_table("MyEmoji")

        async with self.engine.begin() as conn:
            return not await conn.run_sync(test2)

    async def query(
        self, eid: int, default: Optional[Union[Callable[[int], str], str]] = None
    ) -> str:
        """
        The query function takes an emoji ID and returns the corresponding string.
        If no emoji is found, it will return string identified by `default`.

        :param eid: Used to identify the emoji.
        :param default: Used to specify a default value, defaults to return str(eid).
        :return: a string representation of the emoji.
        """

        stmt = select(MyEmoji).where(MyEmoji.eid == eid)
        async with self.sess() as sess:
            result = await sess.execute(stmt)
            r1: Optional[MyEmoji] = result.scalar()
            if r1:
                return cast(str, r1.text)
            stmt = select(EmojiOrm).where(EmojiOrm.eid == eid)
            result = await sess.execute(stmt)
        r2: Optional[EmojiOrm] = result.scalar()
        if r2:
            return cast(str, r2.text)
        if default is None:
            return str(eid)
        if callable(default):
            return default(eid)
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
                result = await sess.execute(select(MyEmoji).where(MyEmoji.eid == eid))
                prev = result.scalar()
                if prev:
                    # if exist: update
                    prev.text = text
                else:
                    # not exist: add
                    sess.add(MyEmoji(eid=eid, text=text))
            await sess.commit()

    async def update(self, engine: AsyncEngine):
        """
        The update function is used to update the database with new data.
        It drops `Emoji` table in current database, and import all data from the given engine.

        :param engine: Engine to a new database to get data from.
        :return: None.
        """

        sess = sessionmaker(engine, class_=AsyncSession)
        stmt = select(EmojiOrm)
        async with self.engine.begin() as conn:
            # drop if exists, and create again
            await conn.run_sync(
                lambda c: sa.inspect(c).has_table(EmojiOrm.__tablename__)
                and EmojiOrm.__table__.drop(c)
                or EmojiOrm.metadata.create_all(c)
            )
        async with self.sess() as os, os.begin():
            async with sess() as ns:
                objs = (await ns.execute(stmt)).scalars().all()
            # TODO: waiting for improvement
            os.add_all([EmojiOrm(eid=i.eid, text=i.text) for i in objs])
            await os.commit()
