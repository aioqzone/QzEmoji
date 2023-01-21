import argparse
import asyncio
import logging
from os import environ as env
from pathlib import Path
from sys import stderr

import yaml
from packaging.version import Version

from qzemoji.base import AsyncEngineFactory
from qzemoji.orm import EmojiOrm, EmojiTable

DB_PATH = Path("data/emoji.db")
DEBUG = bool(env.get("RUNNER_DEBUG"))


def prepare(source: Path, out: Path):
    # exist_ok added in 3.5, god
    if not source.exists():
        raise FileNotFoundError(source)
    with open(source, encoding="utf8") as f:
        v: dict = next(yaml.safe_load_all(f))
    semver: str = v.get("version", "0.1")

    out = out.with_name(f"{out.stem}-{semver}.db")  # force add version tag to filename
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        # missing_ok added in 3.8, so test manually
        out.unlink()
    return out


async def dump_items(source: Path, out: Path):
    with open(source, encoding="utf8") as f:
        v, d = yaml.safe_load_all(f)
        assert isinstance(v, dict)
        assert isinstance(d, dict)
    semver: str = v.get("version", "0.1")

    async with AsyncEngineFactory.sqlite3(out) as engine:
        tbl = EmojiTable(engine)
        await tbl.create()
        async with tbl.sess() as sess:
            async with sess.begin():
                for eid, text in d.items():
                    if not text:
                        log.warning(f"{eid} null value. Skipped.")
                        continue
                    sess.add(EmojiOrm(eid=eid, text=text))
            await tbl.set_version(Version(semver), sess=sess, flush=True)

    return semver


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
    semver = asyncio.run(dump_items(arg.file, arg.out), debug=arg.debug)

    print(semver)
