__author__ = 'zieghailo'
from trimath import triangle_sum
import numpy as np

class Triangle(object):

    def __init__(self, verts):
        """
        Initializes the vertices, the color and the error of the triangle.
        :param verts: a set of Points.
        :return:
        """
        self._vertices = verts
        self._flatten_vertices()

        self._color = None
        self._error = None

    @property
    def vertices(self):
        return self._vertices

    @property
    def flat_vertices(self):
        return self._flat_vertices

    @property
    def color(self):
        return self._color

    @property
    def error(self):
        return self._error

    def colorize(self, img):
        self._color, self._error = triangle_sum(img, self.flat_vertices, get_error=True)

    def _flatten_vertices(self):
        self._flat_vertices = np.zeros([2, 3])

        for i, v in enumerate(self.vertices):
            self._flat_vertices[:, i] = [v.x, v.y]