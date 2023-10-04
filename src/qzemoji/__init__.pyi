from os import PathLike
from pathlib import Path
from typing import Optional

__all__ = ["auto_update", "query", "set", "export"]

enable_auto_update: bool

async def auto_update(): ...
async def query(eid: int) -> Optional[str]: ...
async def set(eid: int, text: str) -> None: ...
async def export(path: PathLike, full: bool = True) -> Path: ...
