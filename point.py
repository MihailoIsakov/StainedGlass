__author__ = 'zieghailo'
import numpy as np

class Point(object):

    def __init__(self, max_x, max_y, x=np.nan, y=np.nan):
        self._position = np.zeros(2)
        if max_x is not None and max_y is not None:
            # the user wants to create a random point
            self._randomize(max_x, max_y)
            self._maxx = max_x
            self._maxy = max_y
        elif not np.isnan(x) and not np.isnan(y):
            # if the user wants to set specific values
            self.x = x
            self.y = y

        self._triangles = set([])
        self._error = np.nan
        self._direction = {'x': None, 'y': None}
        self._least_error = np.inf
        self._best_position = {x: None, y: None}
        self._randomize_direction()

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
    def triangles(self):
        return self._triangles

    @property
    def error(self):
        # self._calc_error()
        return self._error

    def _calc_error(self):
        error = 0
        for t in self._triangles:
            try:
                error += t.error
            except TypeError:
                pass
        self._error = error
        if error < self._least_error:
            self._least_error = error
            self._best_position = {'x': self.x, 'y': self.y}

    def add_triangle(self, triangle):
        self._triangles.add(triangle)
        self._calc_error()

    def remove_triangle(self, triangle):
        try:
            self._triangles.discard(triangle)
        except KeyError:
            print("KeyError: attempted to remove a triangle not in set")
        self._calc_error()

    def move(self, delta=0.1, epsilon=0.1):
        print self._direction
        self.x += self._direction['x'] * delta
        self.x = max(0, min(self.x, self._maxx))
        self.y += self._direction['y'] * delta
        self.y = max(0, min(self.y, self._maxy))

        dx = self._best_position['x'] - self._direction['x']
        dy = self._best_position['y'] - self._direction['y']
        n = np.sqrt(dx*dx + dy*dy)
        dx *= epsilon / n
        dy *= epsilon / n

        self._direction['x'] += dx
        self._direction['y'] += dy
        x = self._direction['x']
        y = self._direction['y']
        n = np.sqrt(x*x + y*y)
        self._direction['x'] / n
        self._direction['y'] / n

        self._least_error *= 1.1

    def _randomize(self, maxx, maxy):
        self.x = np.random.rand() * maxx
        self.y = np.random.rand() * maxy

    def _randomize_direction(self):
        self._direction = {
            'x': np.random.rand() * 2 - 1,
            'y': np.random.rand() * 2 - 1
        }

