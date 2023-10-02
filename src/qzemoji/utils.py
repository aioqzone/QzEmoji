import re
from pathlib import Path
from typing import Optional, Union

from yarl import URL

import qzemoji as qe


def resolve(*, url: Union[URL, str, None] = None, tag: Optional[str] = None):
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


def wrap_plain_text(name: str, fmt="[/{name}]") -> str:
    """This function wraps the given `name` with the given `fmt`, if it is not a pure emoji word.

    :param name: the customized emoji name.
    :param fmt: a format string in ``{`` style, default as ``[/{name}]``.
    :return: The emoji itself if it is a pure emoji word, otherwise a string wrapped by the `fmt`.
    """
    if re.fullmatch(r"[^\u0000-\uFFFF]*", name):
        return name
    return fmt.format(name=name)


async def query_wrap(eid: int, fmt="[/{name}]") -> str:
    """This function query the given eid and wraps it if it is not a pure emoji word. If the name is not
    stored in the database, then it will return a ``[/em]`` tag.

    :return: a ``[/em]`` tag if query has no result, otherwise a wrapped name.

    .. seealso:: :meth:`wrap_plain_text`, :meth:`~qzemoji.utils.build_tag`
    """
    name = await qe.query(eid)
    if name is None:
        return build_tag(eid)
    return wrap_plain_text(name, fmt=fmt)
