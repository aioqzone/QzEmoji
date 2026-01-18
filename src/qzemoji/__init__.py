"""
>>> import qzemoji as qe
>>> import qzemoji.utils as qeu
>>> qeu.resolve(url='http://qzonestyle.gtimg.cn/qzone/em/e400343.gif')
400343
>>> await qe.query(400343)
'🐷'
"""

import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, TypeVar

from typing_extensions import Concatenate, ParamSpec

from .base import AsyncEngineFactory
from .finddb import FindDB
from .orm import EmojiTable

__all__ = ["auto_update", "query", "set", "export"]


enable_auto_update = True
__singleton__: EmojiTable | None = None

P = ParamSpec("P")
T = TypeVar("T")


async def __single__() -> EmojiTable:
    """Init a singleton: a :class:`EmojiTable` instance."""
    global __singleton__
    if __singleton__ is None:
        __singleton__ = EmojiTable(AsyncEngineFactory.sqlite3(await FindDB.find()).engine)
        await __singleton__.create()
        assert not await __singleton__.is_corrupt()
    return __singleton__


async def auto_update():
    global enable_auto_update
    if enable_auto_update:
        try:
            await FindDB.download(proxy=None)  # use env proxy
        finally:
            enable_auto_update = False

        if not FindDB.predefined.exists():
            return

        async with AsyncEngineFactory.sqlite3(FindDB.predefined) as engine:
            await (await __single__()).update(engine)
        FindDB.predefined.unlink()


def auto_update_decorator(
    meth: Callable[Concatenate[EmojiTable, P], Awaitable[T]],
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(meth)
    async def auto_update_wrapper(*args: P.args, **kwds: P.kwargs) -> T:
        await auto_update()
        return await meth(await __single__(), *args, **kwds)

    return auto_update_wrapper


def close():
    global __singleton__
    if __singleton__ is not None:
        asyncio.run(__singleton__.engine.dispose())
        __singleton__ = None


query = auto_update_decorator(EmojiTable.query)
set = auto_update_decorator(EmojiTable.set)
export = auto_update_decorator(EmojiTable.export)
