import asyncio
from pathlib import Path

import aiofiles
from aiohttp import ClientSession

ROOT = Path('data/emoji')
verbose = False


async def emoji_bytes(i: int, ignore_exist=True):
    p = ROOT / f"{i}.png"

    if p.exists():
        if ignore_exist: return
        async with aiofiles.open(p, 'rb') as f:
            return await f.read()

    async with ClientSession() as sess:
        for ext in ['png', 'gif']:
            async with sess.get(f"http://qzonestyle.gtimg.cn/qzone/em/e{i}.{ext}") as r:
                if r.status != 200: 
                    if verbose: print(f'failed: {i}')
                    continue
                return await r.content.read()


async def dl_emoji(i: int):
    b = await emoji_bytes(i)
    if b is None: return 0

    p = ROOT / f"{i}.png"
    async with aiofiles.open(p, 'wb') as f:
        await f.write(b)
        if verbose: print(p.as_posix())
        return 1


def async_dl(*eid: int):
    ROOT.mkdir(parents=True, exist_ok=True)
    loop = asyncio.new_event_loop()
    future = asyncio.gather(*(dl_emoji(i) for i in eid), loop=loop)
    si = loop.run_until_complete(future)
    print(f"{sum(si)} downloaded.")


if __name__ == '__main__':
    # 403140
    for i in range(100, 2500, 500):
        async_dl(*range(i, i + 500))
