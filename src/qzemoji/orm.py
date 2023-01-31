import asyncio
from hashlib import sha256
from os import PathLike
from pathlib import Path
from typing import Optional, cast

import sqlalchemy as sa
import yaml
from sqlalchemy import select
from sqlalchemy.engine import Inspector
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker as sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from .base import AsyncSessionProvider


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class EmojiOrm(Base):
    __tablename__ = "Emoji"

    eid: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    text: Mapped[str] = mapped_column(sa.VARCHAR)


class MyEmoji(Base):
    __tablename__ = "MyEmoji"

    eid: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    text: Mapped[str] = mapped_column(sa.VARCHAR)


class EmojiTable(AsyncSessionProvider):
    async def create(self, conn=None):
        """
        The create function creates `Emoji` and `MyEmoji` table in the database.
        It takes no arguments and returns nothing.

        :param conn: use this connection, otherwise we will create one and close it on return.
        """
        return await self._create(Base, conn=conn)

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
            r1 = await sess.scalar(stmt)
            if r1:
                return r1.text
            stmt = select(EmojiOrm).where(EmojiOrm.eid == eid)
            r2 = await sess.scalar(stmt)
        if r2:
            return r2.text

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
                prev = await sess.scalar(select(MyEmoji).where(MyEmoji.eid == eid))
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

        .. versionchanged:: 4.1.0.dev3

            update `Version` table as well
        """

        sess = sessionmaker(engine)
        stmt = select(EmojiOrm)

        def clear_o_table(c: sa.Connection):
            isp: Optional[Inspector] = sa.inspect(c)
            assert isp is not None
            if isp.has_table(EmojiOrm.__tablename__):
                cast(sa.Table, EmojiOrm.__table__).drop(c)
            EmojiOrm.metadata.create_all(c)

        def check_n_table(c: sa.Connection):
            isp: Optional[Inspector] = sa.inspect(c)
            assert isp.has_table(EmojiOrm.__tablename__), "Incoming database has no `Emoji` table."

        async with self.engine.begin() as oc, engine.begin() as nc:
            # drop if exists, and create again
            await asyncio.gather(oc.run_sync(clear_o_table), nc.run_sync(check_n_table))

        async with self.sess() as os:
            async with sess() as ns:
                objs = (await ns.scalars(stmt)).all()
            async with os.begin():
                os.add_all([EmojiOrm(eid=i.eid, text=i.text) for i in objs])
            await os.commit()

    async def export(self, path: PathLike, full: bool = True) -> Path:
        """Export emoji table to a yaml file. User may start a PR with this file.

        :param path: Where to export
        :param full: If data in `Emoji` table should be export. Keep this value as True if you'd like to submit a PR.
        :return: export path

        .. versionchanged:: 4.0.0

            path is not optional
        """
        stmp = select(MyEmoji)
        stmg = select(EmojiOrm)
        async with self.sess() as sess:
            if full:
                # rp, rg = await asyncio.gather(sess.scalars(stmp), sess.scalars(stmg))
                # BUG: asyncio.gather broken
                rp = await sess.scalars(stmp)
                rg = await sess.scalars(stmg)
            else:
                rp = await sess.scalars(stmp)
                rg = ()  # just suppress warning

        d = {o.eid: o.text for o in rg}
        d.update({o.eid: o.text for o in rp})

        if not isinstance(path, Path):
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf8") as f:
            yaml.safe_dump(d, f, sort_keys=True, allow_unicode=True)
        return path

    async def sha256(self) -> str:
        """Calculate sha256 of ``Emoji`` table.

        :return: sha256 in lower case.

        .. versionadded:: 5.0.0
        """
        statement = select(EmojiOrm)
        async with self.sess() as sess:
            r = await sess.scalars(statement)

        d = {o.eid: o.text for o in r}
        s = ";".join(f"{k}={d[k]}" for k in sorted(d))
        return sha256(s.encode("utf8")).hexdigest().lower()
