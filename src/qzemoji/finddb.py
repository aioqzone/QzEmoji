import asyncio
import re
import shutil
from pathlib import Path
from typing import Optional

from httpx import AsyncClient
from httpx._types import ProxiesTypes
from updater import github as gh
from updater.download import download
from updater.utils import get_latest_asset
from updater.version import parse

from qzemoji.base import AsyncEngineFactory
from qzemoji.orm import EmojiTable


class FindDB:
    """This class can download database from source or find existing database on local storage."""

    download_to = Path("data/emoji.db")
    """Download to this path. After download, the file will be moved to :obj:`.my_db`."""

    my_db = Path("data/myemoji.db")

    @classmethod
    async def download(
        cls, *, client: Optional[AsyncClient] = None, proxy: Optional[ProxiesTypes] = None
    ) -> bool:
        """
        The download function downloads the latest version of the emoji database from GitHub.
        If there is no newer version, it does nothing.

        :param client: use this client, otherwise we will create one and close it on return.
        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :param current_version: Used to check if the current version of the plugin is greater than or equal to the one on GitHub, defaults to None.
        :return: if downloaded.
        """
        if client is None:
            async with AsyncClient(proxies=proxy) as client:
                return await cls.download(client=client, proxy=proxy)

        up = gh.GhUpdater(client, "aioqzone", "QzEmoji")
        online = asyncio.create_task(get_latest_asset(up, "emoji.db", pre=True))

        if cls.my_db.exists():
            async with AsyncEngineFactory.sqlite3(cls.my_db) as engine:
                a, offline = await asyncio.gather(online, EmojiTable(engine).get_version())
            m = re.search(r"EmojiDB: (\d+\.\d+)", a.from_release.body)
            if m and offline and parse(m.group(1)) <= offline:
                return False
        else:
            a = await online

        size = await download(a.download_url, cls.download_to, client=client, proxy=proxy)
        assert size, "db corrupt"
        return True

    @classmethod
    async def find(cls, proxy: Optional[ProxiesTypes] = None) -> Path:
        """
        Find the database file or download if not exists.

        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :return: the path to the database.
        """

        if cls.my_db.exists():
            return cls.my_db
        await cls.download(proxy=proxy)
        shutil.move(cls.download_to, cls.my_db)
        assert cls.my_db.exists()
        return cls.my_db
