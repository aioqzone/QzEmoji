from os import PathLike
from pathlib import Path
from typing import Optional

from .utils import resolve

__all__ = ["auto_update", "resolve", "query", "set", "export"]

proxy: Optional[str]
enable_auto_update: bool
__version__: str

async def auto_update(): ...
async def query(eid: int) -> Optional[str]: ...
async def set(eid: int, text: str) -> None: ...
async def export(path: Optional[PathLike] = None, full: bool = True) -> Path: ...
