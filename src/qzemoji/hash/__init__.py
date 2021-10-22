from dataclasses import dataclass
from pathlib import Path

import cv2 as cv
import numpy as np

from ..collect import collect_items
from .download import ROOT, async_dl

Mat = np.ndarray
mul2 = np.power(2, np.arange(64, dtype=np.int64)[::-1])


def prepare_png():
    async_dl(*(int(Path(k).stem) for k, _ in collect_items()))


def byte_stream():
    """eid, bytes, title
    """
    for k, t in collect_items():
        p = ROOT / str(k)
        try:
            with open(p.with_suffix('.png'), 'rb') as f:
                yield int(p.stem), f.read(), t
        except FileNotFoundError as e:
            print(str(e))
            continue


def b2mat(b: bytes) -> Mat:
    return cv.imdecode(np.frombuffer(b, np.uint8), cv.IMREAD_COLOR)


def dhash_c(img: Mat) -> tuple[Mat, Mat, Mat]:
    """calculate dhash of each channel (BGR)
    """
    dmat: Mat = cv.resize(img, (8, 9), interpolation=cv.INTER_AREA)
    dmat = dmat[:8] > dmat[1:]
    return [i.flatten() for i in np.split(dmat.reshape(64, 3), 3, axis=1)]


def np_stream():
    for eid, b, t in byte_stream():
        buf = np.frombuffer(b, np.uint8)
        yield eid, cv.imdecode(buf, cv.IMREAD_COLOR), t


@dataclass
class EmojiHash:
    text: str
    raw: bytes

    def __post_init__(self):
        img = b2mat(self.raw)
        t = dhash_c(img[4:-4, 3:-3])
        self.rgb = tuple(int((i * mul2).sum()) for i in reversed(t))


def hash_stream():
    for eid, b, t in byte_stream():
        yield eid, EmojiHash(t, b)


if __name__ == '__main__':
    prepare_png()
    for eid, i in hash_stream():
        print(i.text)
