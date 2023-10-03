import re
import shutil
from pathlib import Path
from typing import Optional, Union

from aiofiles import open as aopen
from aiohttp import ClientSession as AsyncClient
from yarl import URL

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
        cls,
        *,
        client: Optional[AsyncClient] = None,
        proxy: Union[str, URL, None] = None,
        buffer_size=4096,
    ) -> bool:
        """
        The download function downloads the latest version of the emoji database from GitHub.
        If there is no newer version, it does nothing.

        :param client: use this client, otherwise we will create one and close it on return.
        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :return: if downloaded.
        """
        if client is None:
            async with AsyncClient(trust_env=proxy is None) as client:
                return await cls.download(client=client, proxy=proxy, buffer_size=buffer_size)

        async def get_online_url() -> Optional[str]:
            r = await client.get(
                "https://aioqzone.github.io/aioqzone-index/simple/qzemoji/index.html", proxy=proxy
            )
            m = re.search(r'<a\s+href="(http.*)">\s*emoji.db\s*</a>', await r.text())
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

        cls.predefined.parent.mkdir(exist_ok=True)
        async with client.get(url, proxy=proxy, allow_redirects=True) as r, aopen(
            cls.predefined, "wb"
        ) as f:
            async for b in r.content.iter_chunked(buffer_size):
                await f.write(b)

        return True

    @classmethod
    async def find(cls, proxy: Union[URL, str, None] = None) -> Optional[Path]:
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
        cls.my_db.parent.mkdir(exist_ok=True)
        shutil.move(cls.predefined.as_posix(), cls.my_db.as_posix())
        assert cls.my_db.exists()
        return cls.my_db
