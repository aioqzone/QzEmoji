import asyncio
from pathlib import Path

import aiofiles
from aiohttp import ClientSession

ROOT = Path('data/emoji')


async def emoji_bytes(i: int, ext: str = 'png', ignore_exist=True):
    p = ROOT / f"{i}.{ext}"
    if p.exists():
        if ignore_exist: return
        async with aiofiles.open(p, 'rb') as f:
            return await f.read()
    async with ClientSession() as sess:
        async with sess.get(f"http://qzonestyle.gtimg.cn/qzone/em/e{i}.{ext}") as r:
            if r.status != 200:
                # print(f'failed: {i}')
                return
            return await r.content.read()


async def dl_emoji(i: int, ext: str = 'png'):
    p = ROOT / f"{i}.{ext}"
    async with aiofiles.open(p, 'wb') as f:
        b = await emoji_bytes(i, ext)
        if b is None: return 0
        await f.write(b)
        return 1


def async_dl(*eid: int):
    loop = asyncio.new_event_loop()
    future = asyncio.gather(*(dl_emoji(i) for i in eid), loop=loop)
    si = loop.run_until_complete(future)
    print(f"{sum(si)} downloaded.")


if __name__ == '__main__':
    # 403140
    if not ROOT.exists(): ROOT.mkdir(parents=True, exist_ok=True)
    for i in range(100, 2500, 500):
        async_dl(*range(i, i + 500))
