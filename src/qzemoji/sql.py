from abc import ABC, abstractproperty
from typing import Callable, Generic, Iterable, Optional, TypeVar, Union

from sqlalchemy.engine import Engine
from sqlalchemy.sql.elements import ColumnElement as ColPred
from sqlmodel import Field, Session, SQLModel, select

RowDef = TypeVar('RowDef')
Primary = TypeVar('Primary')
EmojiID = Union[int, str]


def ensure_eid(eid: EmojiID):
    if isinstance(eid, str): eid = int(eid.split('.')[0])
    assert isinstance(eid, int)
    return eid


class Table(ABC, Generic[Primary, RowDef]):
    order_on: Callable[[RowDef], int] = None

    def __init__(self, engine: Engine, row_ty: RowDef) -> None:
        self.engine = engine
        self.sess = Session(engine)
        self.ty = row_ty

    @abstractproperty
    def pkey(self) -> Primary:
        pass

    def pkey_eq(self, i: Primary) -> tuple[ColPred]:
        return (self.pkey == i, )

    def createTable(self, index: Iterable[str] = None):
        self.ty.metadata.create_all(self.engine)

    def __getitem__(self, i: Primary) -> Optional[RowDef]:
        state = select(self.ty).where(*self.pkey_eq(i))
        row = self.sess.execute(state).first()
        if row and len(row): return row[0]

    def add(self, data: RowDef):
        self.sess.add(data)
        return data

    def __delitem__(self, i: Primary):
        i = Table.__getitem__(self, i)
        if i is None: return
        self.sess.delete(i)

    def __contains__(self, i: Primary):
        return Table.__getitem__(self, i)

    def find(self, cond_sql: ColPred = None, order: Callable[[RowDef], int] = None):
        state = select(self.ty)
        if cond_sql is not None: state = state.where(cond_sql)
        r = self.sess.execute(state).all()
        r = (i[0] for i in r)
        if order: r = sorted(r, key=order)
        return list(r)

    def __iter__(self):
        yield from self.find(order=self.order_on)

    def __del__(self):
        self.sess.close()


class EmojiTable(Table):
    class Emoji(SQLModel, table=True):
        eid: int = Field(primary_key=True)
        text: str

    def __init__(self, engine: Engine) -> None:
        self.order_on = lambda i: i.eid
        super().__init__(engine, self.Emoji)
        self.createTable()

    @property
    def pkey(self) -> Primary:
        return self.Emoji.eid

    def __getitem__(self, eid: EmojiID) -> Optional[str]:
        eid = ensure_eid(eid)
        row = super().__getitem__(eid)
        return row and row.text

    def __setitem__(self, k: EmojiID, text: str):
        k = ensure_eid(k)
        data = self.Emoji(eid=k, text=text)
        return super().add(data)

    def __contains__(self, eid: EmojiID):
        eid = ensure_eid(eid)
        return super().__contains__(eid)


class HashTable(Table):
    class EmojiHash(SQLModel, table=True):
        R: int = Field(primary_key=True)
        G: int = Field(primary_key=True)
        B: int = Field(primary_key=True)
        text: str

    def __init__(self, engine: Engine) -> None:
        super().__init__(engine, self.EmojiHash)
        self.createTable()

    @property
    def pkey(self) -> Primary:
        return self.EmojiHash.R, self.EmojiHash.G, self.EmojiHash.B

    def pkey_eq(self, i: tuple[int, int, int]):
        r, g, b = i
        return self.EmojiHash.R == r, self.EmojiHash.G == g, self.EmojiHash.B == b

    def add(self, data: EmojiHash):
        r, g, b = data.rgb
        data = self.EmojiHash(R=r, G=g, B=b, text=data.text)
        return super().add(data)

    def find(self, text: str):
        return super().find(self.EmojiHash.text == text)
