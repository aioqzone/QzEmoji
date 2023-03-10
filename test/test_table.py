from pathlib import Path

import pytest
import yaml

import qzemoji as qe
import qzemoji.utils as qeu
from qzemoji.base import AsyncEngineFactory
from qzemoji.finddb import FindDB
from qzemoji.orm import EmojiTable

pytestmark = pytest.mark.asyncio


async def test_resolve():
    assert 400343 == qeu.resolve(url="http://qzonestyle.gtimg.cn/qzone/em/e400343.gif")
    assert 400343 == qeu.resolve(tag="[em]e400343[/em]")
    pytest.raises(AssertionError, qeu.resolve, url="", tag="")
    pytest.raises(ValueError, qeu.resolve, tag="[em] e400343[/em]")


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


async def test_sha256():
    async with AsyncEngineFactory.sqlite3(FindDB.my_db) as local, AsyncEngineFactory.sqlite3(
        None
    ) as mem:
        h1 = await EmojiTable(local).sha256()
        mem_table = EmojiTable(mem)
        await mem_table.update(local)
        h2 = await mem_table.sha256()
        assert h1 == h2

        await mem_table.set(100, "hello")
        h3 = await mem_table.sha256()
        assert h2 == h3


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
