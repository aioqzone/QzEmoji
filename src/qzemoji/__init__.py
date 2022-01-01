from pathlib import Path
from urllib.parse import urlparse

from sqlmodel import create_engine
from updater import github as gh

from .sql import EmojiID, EmojiTable
from .utils import ShareNone

__all__ = ['query', 'resolve']
with open(Path(__file__).with_name('VERSION')) as f:
    __version__ = f.read()

db = None


class DBMgr:
    _proxy: dict = None     # proxy dict with auth. (https only)
    _dbpath: Path = None
    enable_auto_update = True

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        if self.enable_auto_update: self.autoUpdate(db_path)

    @classmethod
    def register_proxy(cls, proxy: str, auth: dict = None):
        cls._proxy = gh.register_proxy(proxy, auth)

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
            _db = create_engine(
                'sqlite:///' + self._dbpath.as_posix(), connect_args={'check_same_thread': False}
            )
            self._tbl = EmojiTable(_db)
        return self._tbl

    @classmethod
    @ShareNone
    def autoUpdate(cls, download_to: str, size_callback=None, force: bool = False):
        """update database from Github

        Args:
            download_to (str): download local path
            size_callback (Callable[[int], None], optional): Callback to recv download size. Defaults to None.
            force (bool): download latest database without checking version
        """
        from updater.utils import get_latest_asset
        from updater.version import parse

        try:
            download_to: Path = cls.searchDB(download_to)
        except FileNotFoundError:
            force = True
            download_to = Path(__file__).parent / download_to

        up = gh.GhUpdater(gh.Repo('JamzumSum', 'QzEmoji'))
        a = get_latest_asset(up, 'emoji.db', pre=True)
        if not force and parse(a.from_tag) <= parse(__version__):
            cls.enable_auto_update = False
            return

        from updater.download import download
        for i in download(a.download_url, download_to.with_suffix('.tmp'), proxies=cls._proxy):
            if size_callback: size_callback(i)

        download_to.with_suffix('.tmp').replace(download_to)
        cls.enable_auto_update = False


def query(name: EmojiID, db_path: str = None):
    """lookup for the emoji name.

    Args:
        `name` (EmojiID): id.ext
        `db_path` (str): database path. Default as `data/emoji.db`

    Raises:
        `ValueError`: if `name` cannot be cast to a integer id.
        `FileNotFoundError`: if `db_path` not found.

    Example:
    >>> from qzemoji import query
    >>> query('400343.gif')
    '🐷'
    >>> query(125)
    '困'
    """
    global db
    if db:
        if db_path: db.update_db(db_path)
    else:
        db = DBMgr(db_path or 'data/emoji.db')
    return db.table[name]


def resolve(url: str):
    """resolve a url to `EmojiID.ext`

    Args:
        url (str): emoji url

    Returns:
        str: emoji filename w/o prefex 'e'

    Example:
    >>> from qzemoji import resolve
    >>> resolve('http://qzonestyle.gtimg.cn/qzone/em/e400343.gif')
    400343
    """
    name = Path(urlparse(url).path).stem
    if name.startswith('e'): name = name[1:]
    return int(name)
