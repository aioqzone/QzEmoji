from functools import wraps
from threading import Lock
from typing import Callable


class UnblockLock:
    _lock = Lock()
    acquire = _lock.acquire
    release = _lock.release
    locked = _lock.locked

    def __enter__(self):
        return self.acquire(blocking=False)

    def __exit__(self, *exc):
        if self.locked(): self.release()


def ShareNone(func: Callable):
    lock = UnblockLock()

    @wraps(func)
    def share_wrapper(*args, **kwds):
        with lock as i:
            if i:
                func(*args, **kwds)
            else:
                lock.acquire()
                lock.release()

    return share_wrapper
