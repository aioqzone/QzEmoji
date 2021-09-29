import sqlite3
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar, Union

T = TypeVar('T')


def arglike(i):
    return f"'{i}'" if isinstance(i, str) else \
        str(int(i)) if isinstance(i, bool) else \
        str(i)


class Table:
    order_on = None

    def __init__(
        self,
        name: str,
        cursor: sqlite3.Cursor,
        key: Dict[str, Any],
        pkey: str
    ) -> None:
        pkey = pkey
        assert pkey and pkey in key
        self.name = name
        self.cursor = cursor
        self.key = key
        self.pkey = pkey

    def createTable(self, index: list = None):
        args = ','.join(f"{k} {v}" for k, v in self.key.items())
        self.cursor.execute(f"create table if not exists {self.name} ({args});")
        if index:
            args = ','.join(index)
            self.cursor.execute(
                f"create index if not exists {self.name}_idx on {self.name} ({args});"
            )
        return self

    def __getitem__(self, i):
        self.cursor.execute(
            f'select * from {self.name} WHERE {self.pkey}={arglike(i)};'
        )
        if (r := self.cursor.fetchone()) is None: return
        return dict(zip(self.key, r))

    def __setitem__(self, k, data: dict):
        assert all(i in self.key for i in data)
        if k in self:
            if self.pkey in data: data.pop(self.pkey)
            vals = ','.join(f"{k}={arglike(v)}" for k, v in data.items())
            self.cursor.execute(
                f'update {self.name} SET {vals} WHERE {self.pkey}={arglike(k)};'
            )
        else:
            ndata = data.copy()
            ndata[self.pkey] = k
            cols = ','.join(ndata)
            vals = ','.join(
                f"'{i}'" if isinstance(i, str) else str(i) for i in ndata.values()
            )
            self.cursor.execute(f'insert into {self.name} ({cols}) VALUES ({vals});')
        return data

    def __delitem__(self, i):
        self.cursor.execute(f'delete from {self.name} WHERE {self.pkey}={arglike(i)};')

    def __contains__(self, i):
        return bool(Table.__getitem__(self, i))

    def find(self, cond_sql: str = '', order=None):
        if cond_sql: cond_sql = 'WHERE ' + cond_sql
        order = f'ORDER BY {order}' if order else ''
        keys = list(self.key.keys())
        if hasattr(self, 'parent'):
            i = keys.index(self.pkey)
            keys[i] = f"{self.parent[0].name}.{keys[i]}"
        cols = ','.join(keys)

        self.cursor.execute(f'select {cols} from {self.name} {cond_sql} {order};')
        return [{k: v for k, v in zip(self.key, i)} for i in self.cursor.fetchall()]

    def __mul__(self, tbl):
        assert self.pkey == tbl.pkey
        key = self.key.copy()
        key.update(tbl.key)
        r = Table(
            f'{self.name} LEFT OUTER JOIN {tbl.name} USING ({self.pkey})', self.cursor,
            key, self.pkey
        )
        r.parent = self, tbl
        return r

    def __iter__(self):
        yield from self.find(order=self.order_on)


EmojiID = Union[int, str]


class EmojiTable(Table):
    def __init__(self, name: str, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            name,
            cursor, {
                'id': 'INT PRIMARY KEY',
                'text': 'VARCHAR NOT NULL',
                'ext': 'CHAR[3] NOT NULL'
            },
            pkey='id'
        )
        self.createTable()

    def __getitem__(self, emoji: EmojiID) -> Optional[str]:
        if isinstance(emoji, str):
            emoji = int(emoji.split('.')[0])
        assert isinstance(emoji, int)
        row = super().__getitem__(emoji)
        return row and row['text']

    def __setitem__(self, k: str, text: str):
        k = k.split('.')
        if len(k) != 2:
            k = [k[0], ' ' * 3]
        data = dict(id=int(k[0]), ext=k[1], text=text)
        return super().__setitem__(data['id'], data)

    def __contains__(self, emoji: EmojiID):
        if isinstance(emoji, str):
            emoji = int(emoji.split('.')[0])
        assert isinstance(emoji, int)
        return super().__contains__(emoji)
