__author__ = 'zieghailo'
import trimath

class Triangle(object):

    def __init__(self, verts):
        """
        Initializes the vertices, the color and the error of the triangle.
        :param verts: a set of Points.
        :return:
        """
        self.vertices = verts
        self.color = (0, 0, 0)
        self.error = 0

    @property
    def vertices(self):
        return self.vertices

    @vertices.setter
    def vertices(self, val):
        self.vertices = val

    @property
    def color(self):
        if self.color is None:
            self.color = trimath.triangle_sum()

    def colorize(self):
        trimath.triangle_sum()



