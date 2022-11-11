from pathlib import Path

import pytest
import yaml
from packaging.version import Version

import qzemoji as qe
from qzemoji.base import AsyncEngineFactory
from qzemoji.finddb import FindDB
from qzemoji.orm import EmojiTable

pytestmark = pytest.mark.asyncio


async def test_resolve():
    assert 400343 == qe.resolve(url="http://qzonestyle.gtimg.cn/qzone/em/e400343.gif")
    assert 400343 == qe.resolve(tag="[em]e400343[/em]")
    pytest.raises(AssertionError, qe.resolve, url="", tag="")
    pytest.raises(ValueError, qe.resolve, tag="[em] e400343[/em]")


async def test_autoUpdate():
    await qe.auto_update()
    assert qe.enable_auto_update == False


async def test_update():
    await FindDB.download()
    async with AsyncEngineFactory.sqlite3(
        FindDB.my_db, echo=True
    ) as local, AsyncEngineFactory.sqlite3(None) as mem:
        mem_table = EmojiTable(mem)
        await mem_table.update(local)
        assert await mem_table.query(100) != "100"


async def test_version():
    async with AsyncEngineFactory.sqlite3(None) as mem:
        mem_table = EmojiTable(mem)
        z = await mem_table.get_version()
        assert z.major == 0
        assert z.minor == 0

        await mem_table.set_version(Version("2.1"))
        v = await mem_table.get_version()
        assert v.major == 2
        assert v.minor == 1


async def test_hit():
    assert "🐷" == await qe.query(400343)
    assert "困" == await qe.query(125)


async def test_miss():
    assert await qe.query(100)
    assert await qe.query(1) is None


async def test_set():
    tmp = await qe.query(100)
    assert tmp
    await qe.set(100, "阿巴阿巴")
    assert await qe.query(100) == "阿巴阿巴"
    await qe.set(100, tmp)
    assert await qe.query(100) == tmp


async def test_export():
    p = await qe.export(Path("tmp/emoji.yml"))
    assert p.exists()
    with open("tmp/emoji.yml", encoding="utf8") as f:
        d = yaml.safe_load(f)
    for k, v in d.items():
        assert isinstance(k, int)
        assert isinstance(v, str)
