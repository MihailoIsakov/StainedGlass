__author__ = 'zieghailo'
import numpy as np

class Point(object):
    maxx = None
    maxy = None

    def __init__(self, x=np.nan, y=np.nan, is_fixed=False):
        if Point.x is None and Point.y is None:
            raise AttributeError("Point has not set up its borders. Call set_borders on the class Point.")

        self._position = np.zeros(2)
        if not np.isnan(x) and not np.isnan(y):
            # if the user wants to set specific values
            self.x = x
            self.y = y
        else:
            self._randomize()

        self._fixed = is_fixed
        self._error = np.nan
        self._direction = {'x': None, 'y': None}
        self._least_error = np.inf
        self._best_position = {x: None, y: None}
        self._randomize_direction()

    @classmethod
    def set_borders(cls, x, y):
        cls.maxx = x
        cls.maxy = y

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

    def move(self, delta=0.1, epsilon=0.1):
        if self._fixed:
            return

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

    def _randomize(self):
        self.x = np.random.rand() * Point.maxx
        self.y = np.random.rand() * Point.maxy

    def _randomize_direction(self):
        self._direction = {
            'x': np.random.rand() * 2 - 1,
            'y': np.random.rand() * 2 - 1
        }

