import asyncio
import re
import shutil
from pathlib import Path
from typing import Optional

from httpx import AsyncClient
from httpx._types import ProxiesTypes

from qzemoji.base import AsyncEngineFactory
from qzemoji.orm import EmojiTable

FALLBACK_DB = "https://github.com/aioqzone/QzEmoji/releases/download/4.1.1.dev1/emoji.db"


class FindDB:
    """This class can download database from source or find existing database on local storage."""

    predefined = Path("data/emoji.db")
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
            async with AsyncClient(proxies=proxy, follow_redirects=True) as client:
                return await cls.download(client=client, proxy=proxy)

        async def get_online_url() -> Optional[str]:
            r = await client.get(
                "https://aioqzone.github.io/aioqzone-index/simple/qzemoji/index.html"
            )
            m = re.search(r'<a\s+href="(http.*)">\s*emoji.db\s*</a>', r.text)
            return m and m.group(1)

        url = None
        if cls.my_db.exists():
            url = await get_online_url()
            if url:
                m = re.search(r"#sha256=(\w+)", url)
                if m:
                    async with AsyncEngineFactory.sqlite3(cls.my_db) as engine:
                        if m.group(1).lower() == await EmojiTable(engine).sha256():
                            return False
                        else:
                            url = url[: url.find("#")]
        if url is None:
            url = FALLBACK_DB

        async with client.stream("GET", url) as r:
            with open(cls.predefined, "wb") as f:
                async for b in r.aiter_bytes():
                    f.write(b)

        return True

    @classmethod
    async def find(cls, proxy: Optional[ProxiesTypes] = None) -> Optional[Path]:
        """
        Find the database file or download if not exists.

        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :return: the path to the database, or None if download error.
        """

        if cls.my_db.exists():
            return cls.my_db

        try:
            await cls.download(proxy=proxy)
        except:
            return

        # my_db not exist, so move will not overwrite
        shutil.move(cls.predefined.as_posix(), cls.my_db.as_posix())
        assert cls.my_db.exists()
        return cls.my_db
