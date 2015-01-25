__author__ = 'zieghailo'
import numpy as np
from collections import deque


class Point(object):
    maxx = None
    maxy = None

    def __init__(self, x=None, y=None, is_fixed=False):
        if Point.maxx is None and Point.maxy is None:
            raise AttributeError("Point has not set up its borders. Call set_borders on the class Point.")

        self._position = np.zeros(2)
        if x is not None and y is not None:
            # if the user wants to set specific values
            self._position = np.array([x, y])
        else:
            self._randomize()

        self._fixed = is_fixed
        self._error = None

        self.past_positions = deque()

    def __del__(self):
        if self._fixed:
            raise RuntimeError("Fixed points cannot be deleted")

    @classmethod
    def set_borders(cls, x, y):
        cls.maxx = x
        cls.maxy = y

    # region setters and getters
    @property
    def x(self):
        return self._position[0]

    @property
    def y(self):
        return self._position[1]

    @x.setter
    def x(self, val):
        self._position[0] = val

    @y.setter
    def y(self, val):
        self._position[1] = val

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val
        self._position = np.clip(self._position, [0, 0], [Point.maxx, Point.maxy])

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, val):
        self._error = val
    # endregion

    def _randomize(self):
        self.x = np.random.rand() * Point.maxx
        self.y = np.random.rand() * Point.maxy