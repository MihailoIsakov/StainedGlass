__author__ = 'zieghailo'

import numpy as np

from point import Point


class PSOPoint(Point):

    def __init__(self, x=None, y=None, is_fixed=False):
        Point.__init__(self, x, y, is_fixed)

        self._least_error = np.inf
        self._best_position = np.copy(self._position)
        self._randomize_direction()

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

    def _randomize_direction(self):
        self._direction = np.random.rand(2) * 2 - 1
        norm = np.linalg.norm(self._direction)
        if norm != 0:
            self._direction /= np.linalg.norm(self._direction)
        else:
            self._randomize_direction()
