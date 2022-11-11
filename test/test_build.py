import subprocess as sp
import sys
from pathlib import Path

import pytest
import yaml
from updater.utils import parse

from qzemoji.base import AsyncEngineFactory
from qzemoji.orm import EmojiTable

pytestmark = pytest.mark.asyncio


async def test_build():
    r = sp.run(
        ["python", "script/build.py", "-o", "tmp/build.db"],
        executable=sys.executable,
        capture_output=True,
    )
    assert not r.stderr
    ver = r.stdout.decode().rstrip()

    with open("data/emoji.yml", encoding="utf8") as f:
        v, _ = yaml.safe_load_all(f)
    assert ver == v["version"]

    out = Path("tmp/build.db")

    async with AsyncEngineFactory.sqlite3(out) as engine:
        built = EmojiTable(engine)
        assert not await built.is_corrupt()
        assert await built.get_version() == parse(ver)

    out.unlink()
