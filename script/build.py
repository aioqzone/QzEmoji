import argparse
import asyncio
import logging
from os import environ as env
from pathlib import Path
from sys import stderr

import yaml

from qzemoji.base import AsyncEngineFactory
from qzemoji.orm import EmojiOrm, EmojiTable

DB_PATH = Path("data/emoji.db")
DEBUG = bool(env.get("RUNNER_DEBUG"))


def prepare(source: Path, out: Path):
    if not source.exists():
        raise FileNotFoundError(source)

    out = out.with_name(f"{out.stem}.db")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        # missing_ok added in 3.8, so test manually
        out.unlink()
    return out


async def dump_items(source: Path, out: Path):
    with open(source, encoding="utf8") as f:
        d = yaml.safe_load(f)
        assert isinstance(d, dict)

    async with AsyncEngineFactory.sqlite3(out) as engine:
        tbl = EmojiTable(engine)
        await tbl.create()
        async with tbl.sess() as sess, sess.begin():
            for eid, text in d.items():
                if not text:
                    log.warning(f"{eid} null value. Skipped.")
                    continue
                sess.add(EmojiOrm(eid=eid, text=text))

        return await tbl.sha256()


if __name__ == "__main__":
    psr = argparse.ArgumentParser()
    psr.add_argument("file", nargs="?", default="data/emoji.yml", type=Path)
    psr.add_argument(
        "-D", "--debug", help="asyncio debug mode", action="store_true", default=DEBUG
    )
    psr.add_argument("-o", "--out", type=Path, default=DB_PATH, help="output db path")
    arg = psr.parse_args()

    logging.basicConfig(level="DEBUG" if arg.debug else "INFO", stream=stderr)
    log = logging.getLogger(__name__)

    arg.out = prepare(arg.file, arg.out)
    sha256 = asyncio.run(dump_items(arg.file, arg.out), debug=arg.debug)

    print(sha256)
