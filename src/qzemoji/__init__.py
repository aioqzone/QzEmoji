import sqlite3
from pathlib import Path

from .emojitable import EmojiID, EmojiTable

__version__ = '0.2'
__all__ = ['query']

db = None


class DBMgr:
    tbl_name: str = 'emoji'
    proxy: str = None
    _dbpath: Path = None
    enable_auto_update = True

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        if self.enable_auto_update: self.autoUpdate(db_path)

    @staticmethod
    def searchDB(db_path: str):
        # find database
        toplevel = Path(__file__).parent
        pwd = Path('.')
        findin = [pwd, toplevel]
        if toplevel.name == 'src': findin.append(toplevel.parent)

        for i in findin:
            i /= db_path
            if not i.exists(): continue
            return i
        raise FileNotFoundError(db_path)

    @property
    def db_path(self):
        return self._dbpath

    @db_path.setter
    def db_path(self, db_path: str):
        # find database
        i = self.searchDB(db_path)
        if i == self._dbpath: return
        self._dbpath = i
        self._tbl = None

    @property
    def table(self):
        # singleton
        if self._tbl is None:
            _db = sqlite3.connect(self._dbpath.as_posix(), check_same_thread=False)
            self._tbl = EmojiTable(self.tbl_name, _db.cursor())
        return self._tbl

    @classmethod
    def autoUpdate(cls, download_to: str, size_callback=None):
        """update database from Github

        Args:
            download_to (str): download local path
            size_callback (Callable[[int], None], optional): Callback to recv download size. Defaults to None.

        Returns:
            Path | None: If a new db file is downloaded, reture the Path object; else None.
        """
        from updater import github as gh
        from updater.utils import get_latest_asset
        from updater.version import parse

        download_to: Path = cls.searchDB(download_to)
        proxy = None
        if cls.proxy:
            gh.register_proxy(proxy := {'https': cls.proxy})

        up = gh.GhUpdater(gh.Repo('JamzumSum', 'QzEmoji'))
        a = get_latest_asset(up, 'emoji.db', pre=True)
        if parse(a.from_tag) <= parse(__version__):
            cls.enable_auto_update = False
            return

        from updater.download import download
        for i in download(a.download_url, download_to.with_suffix('.tmp'),
                          proxies=proxy):
            if size_callback: size_callback(i)

        download_to.with_suffix('.tmp').replace(download_to)
        cls.enable_auto_update = False
        return download_to


def query(name: EmojiID, db_path: str = None):
    """lookup for the emoji name.

    Args:
        name (EmojiID): id.ext
        db_path (str): database path. Default as `data/emoji.db`

    Raises:
        ValueError: if `name` cannot be cast to a integer id.
        FileNotFoundError: if `db_path` not found.

    Example:
    >>> from qzemoji import query
    >>> query('400343.gif')
    >>> '🐷'
    >>> query(125)
    >>> '困'
    """
    global db
    if db:
        if db_path: db.update_db(db_path)
    else:
        db = DBMgr(db_path or 'data/emoji.db')
    return db.table[name]
