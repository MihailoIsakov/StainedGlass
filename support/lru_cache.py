__author__ = 'kun xi'
"""
Taken from http://www.kunxi.org/blog/2014/05/lru-cache-in-python/
"""

from collections import OrderedDict as _OrderedDict
from support.numpy_hash import hashable as _hashable

CAPACITY = 65536
cache = _OrderedDict()


def get(key):
    """
    Finds the value for the numpy array key.
    Throws KeyError when encountering an unknown key.
    :param key: input into the function whose results we are caching.
    :return: the result of the function, if it has been calculated before.
    """
    key = _hashable(key)
    value = cache.pop(key)
    cache[key] = value
    return value


def set(key, value):
    key = _hashable(key)
    try:
        cache.pop(key)
    except KeyError:
        if len(cache) >= CAPACITY:
            cache.popitem(last=False)
    cache[key] = value