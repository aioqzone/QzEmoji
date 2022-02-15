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
from pathlib import Path
from typing import Optional

from .finddb import FindDB
from .orm import AsyncEnginew
from .orm import EmojiTable
from .utils import resolve

proxy: Optional[str] = None
enable_auto_update = True
query = set = None
__version__ = None

with open(Path(__file__).with_name('VERSION')) as f:
    __version__ = f.read()


async def _table():
    async with AsyncEnginew.sqlite3(await FindDB.find()) as engine:
        yield EmojiTable(engine)


async def _makefuncs():
    global query, set
    if not query:
        tbl = (await _table().__anext__())
        query = tbl.query
        set = tbl.set


async def auto_update():
    global enable_auto_update
    if enable_auto_update:
        try:
            await FindDB.download(proxy, __version__)
        except:
            logging.error("Failed to download database", exc_info=True)
        finally:
            enable_auto_update = False


async def init():
    await auto_update()
    await _makefuncs()
