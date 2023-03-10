from os import PathLike
from pathlib import Path
from typing import Optional

from httpx._types import ProxiesTypes

__all__ = ["auto_update", "query", "set", "export"]

proxy: Optional[ProxiesTypes]
enable_auto_update: bool

async def auto_update(): ...
async def query(eid: int) -> Optional[str]: ...
async def set(eid: int, text: str) -> None: ...
async def export(path: PathLike, full: bool = True) -> Path: ...
