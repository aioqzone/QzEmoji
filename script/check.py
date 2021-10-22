import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from pytz import timezone
from qzemoji import DBMgr
from qzemoji.hash import EmojiHash
from qzemoji.hash.download import emoji_bytes
from qzemoji.sql import EmojiTable, HashTable
from sqlmodel import create_engine

TZ = timezone('Asia/Shanghai')


def hash_table(db_path: Path):
    hash_path = db_path.with_suffix('.hash.db')
    hash_conn = create_engine('sqlite:///' + hash_path.as_posix())
    return HashTable(hash_conn)


class HashCheck:
    def __init__(self) -> None:
        self.dbm = DBMgr('data/emoji.db')
        self.htb = hash_table(self.dbm.db_path)

    async def check(self, d: EmojiTable.Emoji):
        eid = d.eid
        text = d.text
        odth = self.htb.find(text)

        if odth is None:
            log.warning(f'[{eid}] not exist.')
            return

        b = await emoji_bytes(eid, ignore_exist=False)
        if b is None:
            log.warning(f"[{eid}] GET failed.")
            return

        curh = EmojiHash(text, b)
        if all((curh.rgb != (i.R, i.G, i.B)) for i in odth):
            log.error(f'[{eid}]({text}) hash check failed.')
        log.info(f"[{eid}] passed.")

    def check_all(self, loop=None):
        return asyncio.gather(*(self.check(d) for d in self.dbm.table), loop=loop)


if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('--prefex', default='check')
    arg = psr.parse_args()

    p = Path('./log')
    p.mkdir(exist_ok=True)
    p = p / (arg.prefex + '_' + datetime.now(TZ).strftime("%Y%m%d_%H%M%S"))
    p = p.with_suffix('.log')

    logging.basicConfig(
        level=logging.WARNING,
        filename=p.as_posix(),
        filemode='w',
        encoding='utf8',
        format='%(message)s'
    )
    log = logging.getLogger('period.emoji.check')

    loop = asyncio.new_event_loop()
    future = HashCheck().check_all(loop)
    loop.run_until_complete(future)

    print(p.as_posix())
