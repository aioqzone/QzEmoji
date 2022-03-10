import argparse
import asyncio
from pathlib import Path
from typing import Dict

import yaml

from qzemoji.orm import AsyncEnginew
from qzemoji.orm import EmojiOrm
from qzemoji.orm import EmojiTable

RAW_ROOT = Path("data/raw")
DB_PATH = Path("data/emoji.db")
YML_EXT = [".yml", ".yaml"]


def prepare():
    # exist_ok added in 3.5, god
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        # missing_ok added in 3.8, so test manually
        DB_PATH.unlink()


def item_stream():
    for p in RAW_ROOT.iterdir():
        if not p.suffix in YML_EXT:
            continue
        with open(p, encoding="utf8") as f:
            d: Dict[int, str] = yaml.safe_load(f)
        yield from d.items()


async def dump_items():
    async with AsyncEnginew.sqlite3(DB_PATH) as engine:
        tbl = EmojiTable(engine)
        await tbl.create()
        async with tbl.sess() as sess:
            async with sess.begin():
                for eid, text in item_stream():
                    if not text:
                        print(f"{eid} null value. Skipped.")
                        continue
                    sess.add(EmojiOrm(eid=eid, text=text))
                await sess.commit()


if __name__ == "__main__":
    psr = argparse.ArgumentParser()
    psr.add_argument("-D", "--debug", help="asyncio debug mode", action="store_true")
    arg = psr.parse_args()

    prepare()
    asyncio.run(dump_items(), debug=arg.debug)
