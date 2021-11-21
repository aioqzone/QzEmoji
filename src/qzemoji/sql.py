from abc import ABC, abstractmethod
from typing import Callable, Iterable, MutableMapping, Optional, Union

from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute as Col
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import ColumnElement as ColPred
from sqlmodel import Field, SQLModel, select

Primary = Col
EmojiID = Union[int, str]


def ensure_eid(eid: EmojiID):
    if isinstance(eid, str): eid = int(eid.split('.')[0])
    assert isinstance(eid, int)
    return eid


class Table(ABC, MutableMapping[Primary, SQLModel]):
    order_on: Callable[[SQLModel], int] = None

    def __init__(self, engine: Engine, row_ty: type[SQLModel], thread_safe=True) -> None:
        self.engine = engine
        self.sess = scoped_session(sessionmaker(engine)) if thread_safe else Session(engine)
        self.ty = row_ty

    @abstractmethod
    def pkey(self, col: Union[type[SQLModel], SQLModel]) -> Union[Col, tuple[Col], Primary]:
        pass

    def pkey_eq(self, i: Primary) -> Iterable[ColPred]:
        cols = self.pkey(self.ty)
        if isinstance(cols, tuple):
            return (c == a for c, a in zip(cols, i))
        else:
            return self.pkey(self.ty) == i,

    def createTable(self):
        self.ty.metadata.create_all(self.engine)

    def __getitem__(self, i: Primary) -> Optional[SQLModel]:
        state = select(self.ty).where(*self.pkey_eq(i))
        row = self.sess.execute(state).first()
        if row and len(row): return row[0]

    def add(self, data: SQLModel):
        self.sess.add(data)
        return data

    def __setitem__(self, i: Primary, data: SQLModel) -> None:
        assert i == self.pkey(data)
        return self.add(data)

    def __delitem__(self, i: Primary):
        i = Table.__getitem__(self, i)
        if i is None: return
        self.sess.delete(i)

    def __contains__(self, i: Primary):
        return Table.__getitem__(self, i)

    def find(self, cond_sql: ColPred = None, order: Callable[[SQLModel], int] = order_on):
        state = select(self.ty)
        if cond_sql is not None: state = state.where(cond_sql)
        r = self.sess.execute(state).all()
        r = (i[0] for i in r)
        if order: r = sorted(r, key=order)
        return list(r)

    def __iter__(self):
        yield from self.find()

    def __del__(self):
        self.sess.close()

    def __len__(self) -> int:
        return super().__len__()


class EmojiTable(Table):
    class Emoji(SQLModel, table=True):
        eid: int = Field(primary_key=True)
        text: str

    def __init__(self, engine: Engine) -> None:
        self.order_on = lambda i: i.eid
        super().__init__(engine, self.Emoji)
        self.createTable()

    def pkey(self, col: Union[type[Emoji], Emoji]):
        return col.eid

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

    def pkey(self, col: Union[type[EmojiHash], EmojiHash]):
        return self.EmojiHash.R, self.EmojiHash.G, self.EmojiHash.B

    def add(self, data: EmojiHash):
        r, g, b = data.rgb
        data = self.EmojiHash(R=r, G=g, B=b, text=data.text)
        return super().add(data)

    def find(self, text: str):
        return super().find(self.EmojiHash.text == text)
