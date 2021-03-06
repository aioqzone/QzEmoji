import re
from pathlib import Path
from typing import Optional

from httpx import URL
from httpx._types import URLTypes


def resolve(*, url: Optional[URLTypes] = None, tag: Optional[str] = None):
    """
    The resolve function takes either a URL or a tag as an argument, and returns the emoji ID.

    If the argument is a URL, it extracts the emoji ID from it.
    If not, it assumes that the argument is already an emoji tag, and extracts its content.

    :param url: a URL where the emoji ID is extracted from.
    :param tag: a tag where the emoji ID is extracted from. e.g. `[em]e400343[/em]`
    :raises AssertionError: if both or none of arguments are/is specified.
    :raises ValueError: if tag doesn't match the pattern.
    :return: emoji ID.

    >>> resolve(url='http://qzonestyle.gtimg.cn/qzone/em/e400343.gif')
    400343
    >>> resolve(tag='[em]e400343[/em]')
    400343
    >>> resolve('no kwargs specified')
    AssertionError
    >>> resolve(tag='[em] e400343[/em]')
    ValueError('[em] e400343[/em]')
    """
    assert (url is None) ^ (tag is None)
    if tag:
        m = re.match(r"\[em\]e(\d+)\[/em\]", tag)
        if not m:
            raise ValueError(tag)
        name: str = m.group(1)
    else:
        assert url
        if isinstance(url, str):
            url = URL(url)
        name = Path(url.path).stem
        if name.startswith("e"):
            # py39- has no removeprefix
            name = name[1:]
    return int(name)


def build_html(eid: int, host: str = "qzonestyle.gtimg.cn", ext: str = "png"):
    return f"http://{host}/qzone/em/e{eid}.{ext}"


def build_tag(eid: int):
    return f"[em]e{eid}[/em]"
