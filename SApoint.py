__author__ = 'zieghailo'

import numpy as np

from point import Point


class SApoint(Point):
    switched = 0
    notswitched = 0

    def __init__(self, x=None, y=None, is_fixed=False):
        Point.__init__(self, x, y, is_fixed=is_fixed)
        self._oldposition = np.copy(self.position)
        self.neighbors = set()
        self.error = 0

    def shift(self, pixtemp):
        if self._fixed:
            return
        # uniform distribution around the old position
        mov = np.array([0, 0])
        while True:
            mov = np.random.rand(2) * 2 - 1
            if sum(mov * mov) <= 1:
                break

        # move it somewhere in the circle with the radius pixtemp
        self.position = self._oldposition + pixtemp * mov

    def accept(self):
        SApoint.switched += 1
        self._oldposition = self._position

    def reset(self):
        SApoint.notswitched += 1
        self._position = self._oldposition