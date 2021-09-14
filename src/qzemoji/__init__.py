import sqlite3
from .emojitable import EmojiID, EmojiTable

_db = _tbl = None
__all__ = ['query']


def findDB(db_path: str):
    # find database
    from pathlib import Path
    toplevel = Path(__file__).parent
    pwd = Path('.')
    findin = [pwd, toplevel]
    if toplevel.name == 'src': findin.append(toplevel.parent)

    for i in findin:
        i /= db_path
        if i.exists():
            return str(i.absolute())
    raise FileNotFoundError(db_path)


def _table(db_path: str = 'data/emoji.db', name: str = 'emoji'):
    global _db, _tbl

    # singleton
    if _tbl is None:
        db_path = findDB(db_path)
        _db = sqlite3.connect(db_path, check_same_thread=False)
        _tbl = EmojiTable(name, _db.cursor())
    return _tbl


def query(name: EmojiID):
    """lookup for the emoji name.

    Args:
        name (EmojiID): id.ext

    Raises:
        ValueError: if `name` cannot be cast to a integer id.
        FileNotFoundError: if `data/emoji.db` not found.

    Example:
    >>> from qzemoji import query
    >>> query('400343.gif')
    >>> '🐷'
    >>> query(125)
    >>> '困'
    """
    return _table()[name]
