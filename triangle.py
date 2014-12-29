__author__ = 'zieghailo'
from trimath import triangle_sum
import numpy as np

class Triangle(object):

    def __init__(self, mesh, verts):
        """
        Initializes the vertices, the color and the error of the triangle.
        :param verts: a set of Points.
        :return:
        """
        self._mesh = mesh
        self._vertices = verts
        self._flatten_vertices()
        self.used = False
        for v in self._vertices:
            v.triangles.add(self)

        self._color = None
        self._error = None

    def delete(self):
        for v in self._vertices:
            try:
                v.triangles.remove(self)
            except ValueError:
                pass

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

    def colorize(self):
        self._color, self._error = triangle_sum(self._mesh.image, self.flat_vertices, get_error=True)

    def _flatten_vertices(self):
        self._flat_vertices = np.zeros([2, 3])

        for i, v in enumerate(self.vertices):
            self._flat_vertices[:, i] = [v.x, v.y]