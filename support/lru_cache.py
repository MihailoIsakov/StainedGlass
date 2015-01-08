__author__ = 'kun xi'
"""
Taken from http://www.kunxi.org/blog/2014/05/lru-cache-in-python/
"""

import collections


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value