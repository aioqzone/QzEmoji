import subprocess as sp
import sys
from hashlib import sha256
from pathlib import Path

import pytest
import yaml

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
    h1 = r.stdout.decode().rstrip()

    with open("data/emoji.yml", encoding="utf8") as f:
        d = yaml.safe_load(f)
    s = ";".join(f"{k}={d[k]}" for k in sorted(d))
    h2 = sha256(s.encode("utf8")).hexdigest().lower()
    assert h1 == h2

    out = Path(f"tmp/build.db")

    async with AsyncEngineFactory.sqlite3(out) as engine:
        built = EmojiTable(engine)
        assert not await built.is_corrupt()
        assert h2 == await built.sha256()

    out.unlink()
