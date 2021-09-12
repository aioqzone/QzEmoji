import sqlite3
from .emojitable import EmojiID, EmojiTable

_db = _tbl = None
__all__ = ['query']


def _table(db_path: str = 'data/emoji.db', name: str = 'emoji'):
    global _db, _tbl
    if _tbl is None:
        _db = sqlite3.connect(db_path)
        _tbl = EmojiTable(name, _db.cursor())
    return _tbl


def query(name: EmojiID):
    """lookup for the emoji name.

    Args:
        name (EmojiID): id.ext

    Raises:
        ValueError: if `name` cannot be cast to a integer id.

    Example:
    >>> from qzemoji import query
    >>> query('400343.gif')
    >>> '🐷'
    >>> query(125)
    >>> '困'
    """
    return _table()[name]
