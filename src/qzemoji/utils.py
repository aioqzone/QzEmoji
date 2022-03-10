from pathlib import Path
import re
from urllib.parse import ParseResult


def resolve(*, url: ParseResult = None, tag: str = None):
    """
    The resolve function takes either a URL or a tag as an argument, and returns the emoji ID.

    If the argument is a URL, it extracts the emoji ID from it.
    If not, it assumes that the argument is already an emoji tag, and extracts its content.

    :param url: a URL where the emoji ID is extracted from.
    :param tag: a tag where the emoji ID is extracted from. e.g. `[em]e400343[/em]`
    :raises AssertionError: if both or none of arguments are/is specified.
    :raises ValueError: if tag doesn't match the pattern.
    :return: emoji ID.

    >>> from urllib.parse import urlparse
    >>> resolve(url=urlparse('http://qzonestyle.gtimg.cn/qzone/em/e400343.gif'))
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
        name = Path(url.path).stem.removeprefix("e")
    return int(name)


def build_html(eid: int, host="qzonestyle.gtimg.cn", ext="png"):
    return f"http://{host}/qzone/em/e{eid}.{ext}"


def build_tag(eid: int):
    return f"[em]e{eid}[/em]"
