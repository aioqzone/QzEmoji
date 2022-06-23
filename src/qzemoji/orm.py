import asyncio
from os import PathLike
from pathlib import Path
from typing import Optional, cast

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from .base import AsyncSessionProvider

Base = declarative_base()


class EmojiOrm(Base):
    __tablename__ = "Emoji"

    eid = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.VARCHAR)


class MyEmoji(Base):
    __tablename__ = "MyEmoji"

    eid = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.VARCHAR)


class EmojiTable(AsyncSessionProvider):
    async def create(self):
        """
        The create function creates `Emoji` and `MyEmoji` table in the database.
        It takes no arguments and returns nothing.
        """
        return await self._create(Base)

    async def is_corrupt(self) -> bool:
        def test2(conn):
            insp = sa.inspect(conn)
            return insp.has_table("Emoji") and insp.has_table("MyEmoji")

        async with self.engine.begin() as conn:
            return not await conn.run_sync(test2)

    async def query(self, eid: int) -> Optional[str]:
        """
        The query function takes an emoji ID and returns the corresponding string.
        If no emoji is found, it will return string identified by `default`.

        :param eid: Used to identify the emoji.
        :param default: Used to specify a default value, defaults to return str(eid).
        :return: a string representation of the emoji, or None if not found.
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

        def do_w_conn(c: AsyncConnection):
            if sa.inspect(c).has_table(EmojiOrm.__tablename__):
                EmojiOrm.__table__.drop(c)
            EmojiOrm.metadata.create_all(c)

        async with self.engine.begin() as conn:
            # drop if exists, and create again
            await conn.run_sync(do_w_conn)

        async with self.sess() as os, os.begin():
            async with sess() as ns:
                ns: AsyncSession
                objs = (await ns.execute(stmt)).scalars().all()
            # TODO: waiting for improvement
            os.add_all([EmojiOrm(eid=i.eid, text=i.text) for i in objs])
            await os.commit()

    async def export(self, path: Optional[PathLike] = None, full: bool = True):
        """Export emoji table to a yaml file. User may start a PR with this file.

        :param full: If data in `Emoji` table should be export. Keep this value as True if you'd like to submit a PR.
        :param path: Where to export, default as `data/emoji.yml`
        :return: export path
        """
        import yaml

        stmp = select(MyEmoji)
        stmg = select(EmojiOrm)
        async with self.sess() as sess:
            if full:
                rp, rg = await asyncio.gather(sess.execute(stmp), sess.execute(stmg))
                rp, rg = rp.scalars(), rg.scalars()
            else:
                rp = (await sess.execute(stmp)).scalars()
                rg = []  # just suppress warning

        d = {o.eid: o.text for o in rg} if full else {}
        d.update({o.eid: o.text for o in rp})

        p = path or Path("data/emoji.yml")
        if not isinstance(p, Path):
            p = Path(p)
        p.parent.mkdir(parents=True, exist_ok=True)

        with open(p, "w", encoding="utf8") as f:
            yaml.dump(d, f, sort_keys=True, allow_unicode=True)
        return p
