import time
import functools
from logger import logger
from typing import Callable


def async_timed():
    def wrapper(async_func: Callable) -> Callable:
        @functools.wraps(async_func)
        async def wrapped(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                return await async_func(*args, **kwargs)
            finally:
                t1 = time.perf_counter()
                logger.info(f"{(t1 - t0):.3f}s - {async_func.__name__}")

        return wrapped

    return wrapper
