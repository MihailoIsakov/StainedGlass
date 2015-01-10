__author__ = 'kun xi'
"""
Taken from http://www.kunxi.org/blog/2014/05/lru-cache-in-python/
"""

import collections
# FIXME maybe use DI, as this is too hardwired?
from support.numpy_hash import hashable


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        """
        Finds the value for the numpy array key.
        Throws KeyError when encountering an unknown key.
        :param key: input into the function whose results we are caching.
        :return: the result of the function, if it has been calculated before.
        """
        key = hashable(key)
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def set(self, key, value):
        key = hashable(key)
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value