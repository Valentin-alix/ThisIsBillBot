import functools
import inspect


def cache(func):
    wrapper = functools.cache(func)
    wrapper.__signature__ = inspect.signature(func)
    return wrapper
