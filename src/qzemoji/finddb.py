from pathlib import Path
import shutil

from updater import github as gh
from updater.download import adownload
from updater.utils import get_latest_asset
from updater.version import parse

REPO = gh.Repo('JamzumSum', 'QzEmoji')


class FindDB:
    """This class can download database from source or find existing database on local storage."""
    download_to = Path('data/emoji.db')

    @classmethod
    async def download(cls, proxy: str = None, current_version: str = None):
        """
        The download function downloads the latest version of the emoji database from GitHub.
        If there is no newer version, it does nothing.
        
        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :param current_version: Used to check if the current version of the plugin is greater than or equal to the one on GitHub, defaults to None.
        :return: None.
        """

        if proxy: gh.register_proxy(proxy)
        up = gh.GhUpdater(REPO)
        a = get_latest_asset(up, 'emoji.db', pre=True)
        if current_version and parse(a.from_tag) <= parse(current_version):
            return

        await adownload(a.download_url, cls.download_to, proxy=proxy)
        shutil.copy(cls.download_to, cls.download_to.with_suffix('.db.bak'))

    @classmethod
    async def find(cls, proxy: str = None) -> Path:
        """
        Find the database file or download if not exists.

        :param proxy: Used to pass a proxy to the download function, defaults to None.
        :return: the path to the database.
        """

        if cls.download_to.exists(): return cls.download_to
        await cls.download(proxy)
        assert cls.download_to.exists()
        return cls.download_to
