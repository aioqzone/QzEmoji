from time import sleep

from qzemoji.utils import ShareNone


def test_sharenone():
    @ShareNone
    def inci(_):
        nonlocal i
        i += 1
        sleep(1)

    from concurrent.futures import ThreadPoolExecutor
    i = 0
    ex = ThreadPoolExecutor(3)
    ex.map(inci, range(3))
    assert i == 1
