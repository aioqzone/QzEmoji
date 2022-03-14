from urllib.parse import urlparse

import pytest

import qzemoji as qe

pytestmark = pytest.mark.asyncio


async def test_resolve():
    assert 400343 == qe.resolve(url=urlparse("http://qzonestyle.gtimg.cn/qzone/em/e400343.gif"))
    assert 400343 == qe.resolve(tag="[em]e400343[/em]")
    pytest.raises(AssertionError, qe.resolve, url="", tag="")
    pytest.raises(ValueError, qe.resolve, tag="[em] e400343[/em]")


async def test_autoUpdate():
    await qe.init()
    assert qe.enable_auto_update == False


async def test_update():
    await qe.FindDB.download()
    async with qe.orm.AsyncEnginew.sqlite3(qe.FindDB.download_to, echo=True) as engine:
        tbl = await qe._table().__anext__()
        await tbl.update(engine)
        assert await tbl.query(100) != "100"


async def test_hit():
    assert "🐷" == await qe.query(400343)
    assert "困" == await qe.query(125)


async def test_miss():
    assert await qe.query(0) == "0"
    assert await qe.query(1, "2") == "2"
    assert await qe.query(2, lambda i: f"e{i}") == "e2"


async def test_set():
    await qe.set(3, "阿巴阿巴")
    assert await qe.query(3) == "阿巴阿巴"
