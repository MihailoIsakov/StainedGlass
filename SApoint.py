__author__ = 'zieghailo'

import numpy as np

from point import Point


class SApoint(Point):
    switched = 0
    notswitched = 0

    def __init__(self, x=None, y=None, is_fixed=False):
        Point.__init__(self, x, y, is_fixed=is_fixed)
        self._oldposition = np.copy(self.position)
        self._olderror = np.inf

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

    # @profile
    def evaluate(self):
        if self.error <= self._olderror:
            SApoint.switched += 1
            # the new position is accepted
            self._oldposition = self.position
            self._olderror = self.error
        else:
            SApoint.notswitched += 1
            self.position = self._oldposition
            self.error = np.nan


    def reset(self):
        self.position = self._oldposition

    def accept_error(self):
        self._olderror = self._error