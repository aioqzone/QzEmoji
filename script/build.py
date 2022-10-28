import argparse
import asyncio
import logging
from os import environ as env
from pathlib import Path

import yaml
from packaging.version import Version

from qzemoji.base import AsyncEngineFactory
from qzemoji.orm import EmojiOrm, EmojiTable

DB_PATH = Path("data/emoji.db")
DEBUG = env.get("RUNNER_DEBUG")


def prepare(source: Path):
    # exist_ok added in 3.5, god
    if not source.exists():
        raise FileNotFoundError(source)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        # missing_ok added in 3.8, so test manually
        DB_PATH.unlink()


async def dump_items(source: Path):
    async with AsyncEngineFactory.sqlite3(DB_PATH) as engine:
        tbl = EmojiTable(engine)
        with open(source, encoding="utf8") as f:
            v, d = yaml.safe_load_all(f)
        await tbl.create()
        async with tbl.sess() as sess:
            async with sess.begin():
                for eid, text in d.items():
                    if not text:
                        logging.warning(f"{eid} null value. Skipped.")
                        continue
                    sess.add(EmojiOrm(eid=eid, text=text))
            await tbl.set_version(Version(v.get("version", "0.1")), sess=sess, flush=True)


if __name__ == "__main__":
    psr = argparse.ArgumentParser()
    psr.add_argument("file", nargs="?", default="data/emoji.yml", type=Path)
    psr.add_argument(
        "-D", "--debug", help="asyncio debug mode", action="store_true", default=DEBUG
    )
    arg = psr.parse_args()

    prepare(arg.file)
    asyncio.run(dump_items(arg.file), debug=arg.debug)
