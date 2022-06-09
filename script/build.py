import argparse
import asyncio
from pathlib import Path
from typing import Dict

import yaml

from qzemoji.base import AsyncEngineFactory
from qzemoji.orm import EmojiOrm, EmojiTable

DB_PATH = Path("data/emoji.db")


def prepare(source: Path):
    # exist_ok added in 3.5, god
    if not source.exists():
        raise FileNotFoundError(source)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        # missing_ok added in 3.8, so test manually
        DB_PATH.unlink()


def item_stream(p: Path):
    with open(p, encoding="utf8") as f:
        d: Dict[int, str] = yaml.safe_load(f)
    yield from d.items()


async def dump_items(source: Path):
    async with AsyncEngineFactory.sqlite3(DB_PATH) as engine:
        tbl = EmojiTable(engine)
        await tbl.create()
        async with tbl.sess() as sess:
            async with sess.begin():
                for eid, text in item_stream(source):
                    if not text:
                        print(f"{eid} null value. Skipped.")
                        continue
                    sess.add(EmojiOrm(eid=eid, text=text))
                await sess.commit()


if __name__ == "__main__":
    psr = argparse.ArgumentParser()
    psr.add_argument("-D", "--debug", help="asyncio debug mode", action="store_true")
    psr.add_argument("-f", "--file", help="source file", default="data/emoji.yml", type=Path)
    arg = psr.parse_args()

    prepare(arg.file)
    asyncio.run(dump_items(arg.file), debug=arg.debug)
