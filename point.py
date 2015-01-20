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
        self._least_error = np.inf
        self._best_position = np.copy(self._position)
        self._randomize_direction()

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

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, val):
        self._error = val
        if val < self._least_error:
            self._least_error = val
    # endregion

    def move(self, delta=2, epsilon=1, omega=1.05):
        # the point are practically moving in one dimension
        # they need data in which way to turn. :/ fuck
        if self._fixed:
            return

        self._position += self._direction * delta
        self._position[0] = np.clip(self._position[0], 0, Point.maxx)
        self._position[1] = np.clip(self._position[1], 0, Point.maxy)

        # change direction to point more towards the best position
        d = self._best_position - self._position
        d /= np.linalg.norm(d)
        if not np.isnan(d).any():
            self._direction += d * epsilon
        # TODO possibly normalize it?

        self._least_error *= omega

    def _randomize(self):
        self.x = np.random.rand() * Point.maxx
        self.y = np.random.rand() * Point.maxy

    def _randomize_direction(self):
        self._direction = np.random.rand(2) * 2 - 1
        norm = np.linalg.norm(self._direction)
        if norm != 0:
            self._direction /= np.linalg.norm(self._direction)
        else:
            self._randomize_direction()
