"""
>>> import qzemoji as qe
>>> qe.proxy = "http://localhost:1234"
>>> await qe.init()     # will auto update database, so set a proxy if needed.
>>> qe.resolve(url='http://qzonestyle.gtimg.cn/qzone/em/e400343.gif')
400343
>>> await qe.query(400343)
'🐷'
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Optional, TypeVar

from httpx._types import ProxiesTypes
from typing_extensions import ParamSpec

from .base import AsyncEngineFactory
from .finddb import FindDB
from .orm import EmojiTable
from .utils import resolve

__all__ = ["auto_update", "resolve", "query", "set", "export"]


proxy: Optional[ProxiesTypes] = None
enable_auto_update = True
__version__ = "3.3.1a1.dev1"
__singleton__: EmojiTable = None  # type: ignore

P = ParamSpec("P")
T = TypeVar("T")


async def __single__():
    """Init a singleton: a :class:`EmojiTable` instance."""
    global __singleton__
    if __singleton__ is None:
        __singleton__ = EmojiTable(AsyncEngineFactory.sqlite3(await FindDB.find()).engine)
        await __singleton__.create()
        assert not await __singleton__.is_corrupt()


async def auto_update():
    global enable_auto_update
    if enable_auto_update:
        try:
            if proxy:
                downloaded = await FindDB.download(proxy, __version__)
            else:
                downloaded = await FindDB.download(current_version=__version__)
        except:
            logging.error("Failed to download database", exc_info=True)
            downloaded = False
        finally:
            enable_auto_update = False

        if not downloaded:
            return
        assert FindDB.download_to.exists()

        async with AsyncEngineFactory.sqlite3(FindDB.download_to) as engine:
            return await __singleton__.update(engine)


def auto_update_decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(func)
    async def auto_update_wrapper(*args: P.args, **kwds: P.kwargs):
        await auto_update()
        return await func(*args, **kwds)

    return auto_update_wrapper


asyncio.run(__single__())
query = auto_update_decorator(__singleton__.query)
set = auto_update_decorator(__singleton__.set)
export = auto_update_decorator(__singleton__.export)
