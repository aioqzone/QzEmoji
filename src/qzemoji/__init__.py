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

import logging
from typing import Optional

from .finddb import FindDB
from .orm import AsyncEnginew
from .orm import EmojiTable
from .utils import resolve

proxy: Optional[str] = None
enable_auto_update = True
query = set = None
__version__ = "2.1.1a1"

__all__ = ["auto_update", "init", "resolve", "query", "proxy", "enable_auto_update"]


async def _table():
    async with AsyncEnginew.sqlite3(await FindDB.find()) as engine:
        tbl = EmojiTable(engine)
        await tbl.create()
        assert not await tbl.is_corrupt()
        while True:
            yield tbl


async def _makefuncs():
    global query, set
    if query and set:
        return
    async for tbl in _table():
        query = tbl.query
        set = tbl.set
        return


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
            async for tbl in _table():
                await tbl.update(engine)
                return


async def init():
    await auto_update()
    await _makefuncs()
