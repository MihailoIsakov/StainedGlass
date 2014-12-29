__author__ = 'zieghailo'
import numpy as np

class Point(object):

    def __init__(self, max_x=None, max_y=None, x=np.nan, y=np.nan):
        if max_x is not None and max_y is not None:
            # the user wants to create a random point
            self._randomize(max_x, max_y)
        elif not np.isnan(x) and not np.isnan(y):
            # if the user wants to set specific values
            self.x = x
            self.y = y

        self._triangles = set([])
        self._error = np.nan

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def triangles(self):
        return self._triangles

    @property
    def error(self):
        error = 0
        for t in self._triangles:
            try:
                error += t.error
            except TypeError:
                pass
        return error

    @x.setter
    def x(self, val):
        self._x = val

    @y.setter
    def y(self, val):
        self._y = val

    def add_triangle(self, triangle):
        self._triangles.add(triangle)

    def remove_triangle(self, index):
        try:
            del(self._triangles[index])
        except IndexError:
            print("IndexError: triangle index out of range")


    def _randomize(self, maxx, maxy):
        self.x = np.random.rand() * maxx
        self.y = np.random.rand() * maxy

