__author__ = 'zieghailo'

import numpy as np

from point import Point

class SApoint(Point):

    def __init__(self, x=None, y=None, is_fixed=False):
        Point.__init__(self, x, y, is_fixed=is_fixed)
        self._oldposition = np.copy(self.position)
        self._olderror = np.copy(self.error)

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

    def evaluate(self):
        if self.error < self._olderror:
            # the new position is accepted
            self._oldposition = self.position
            self._olderror = self.error
        else:
            self.position = self._oldposition
            self.error = np.nan


    def reset(self):
        self.position = self._oldposition