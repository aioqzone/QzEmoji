import shutil
from pathlib import Path
from typing import Optional, Union

from httpx import URL, AsyncClient
from updater import github as gh
from updater.download import download
from updater.utils import get_latest_asset
from updater.version import parse

StrOrURL = Union[URL, str]


class FindDB:
    """This class can download database from source or find existing database on local storage."""

    download_to = Path("data/emoji.db")
    my_db = Path("data/myemoji.db")

    @classmethod
    async def download(
        cls, proxy: Optional[StrOrURL] = None, current_version: Optional[str] = None
    ):
        """
        The download function downloads the latest version of the emoji database from GitHub.
        If there is no newer version, it does nothing.

        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :param current_version: Used to check if the current version of the plugin is greater than or equal to the one on GitHub, defaults to None.
        :return: if downloaded.
        """
        client_dict = {}
        if proxy:
            client_dict["proxies"] = proxy
        async with AsyncClient(**client_dict) as client:
            up = gh.GhUpdater(client, "aioqzone", "QzEmoji")

            a = await get_latest_asset(up, "emoji.db", pre=True)

        if current_version and parse(a.from_tag) <= parse(current_version):
            return False

        assert await download(a.download_url, cls.download_to), "db corrupt"
        return True

    @classmethod
    async def find(cls, proxy: Optional[str] = None) -> Path:
        """
        Find the database file or download if not exists.

        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :return: the path to the database.
        """

        if cls.my_db.exists():
            return cls.my_db
        await cls.download(proxy)
        shutil.move(cls.download_to.as_posix(), cls.my_db)
        assert cls.my_db.exists()
        return cls.my_db
