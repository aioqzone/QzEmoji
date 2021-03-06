import asyncio

import pytest

import qzemoji as qe

pytestmark = pytest.mark.asyncio


async def test_async():
    qe.enable_auto_update = False
    done, _ = await asyncio.wait([asyncio.create_task(qe.query(i)) for i in range(100, 200)])
    assert len(done) == 100
