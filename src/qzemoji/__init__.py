"""
>>> from urllib.parse import urlparse
>>> import qzemoji as qe
>>> qe.proxy = "http://localhost:1234"
>>> await qe.init()     # will auto update database, so set a proxy if needed.
>>> qe.resolve(url=urlparse('http://qzonestyle.gtimg.cn/qzone/em/e400343.gif'))
400343
>>> await qe.query(400343)
'🐷'
"""

import asyncio
import logging
from typing import Callable, Optional, Union

from sqlalchemy.ext.asyncio import AsyncEngine

from .finddb import FindDB
from .orm import AsyncEnginew, EmojiTable
from .utils import resolve

proxy: Optional[str] = None
enable_auto_update = True
__version__ = "2.2.0.dev1"

__all__ = ["auto_update", "resolve", "query", "set", "update", "export"]


__singleton__: EmojiTable


async def __init__():
    """Init a singleton: a :class:`EmojiTable` instance."""
    if not "__singleton__" in globals():
        global __singleton__
        __singleton__ = EmojiTable(AsyncEnginew.sqlite3(await FindDB.find()).engine)
        await __singleton__.create()
        assert not await __singleton__.is_corrupt()
        await auto_update()


async def auto_update():
    global enable_auto_update
    if enable_auto_update:
        try:
            downloaded = await FindDB.download(proxy, __version__)
        except:
            logging.error("Failed to download database", exc_info=True)
            downloaded = False
        finally:
            enable_auto_update = False

        if not downloaded:
            return
        assert FindDB.download_to.exists()

        async with AsyncEnginew.sqlite3(FindDB.download_to) as engine:
            return await __singleton__.update(engine)


async def query(eid: int, default: Optional[Union[Callable[[int], str], str]] = None) -> str:
    return await __singleton__.query(eid, default=default)


async def set(eid: int, text: str):
    return await __singleton__.set(eid, text)


async def update(engine: AsyncEngine):
    return await __singleton__.update(engine)


async def export():
    return await __singleton__.export()


asyncio.run(__init__())
