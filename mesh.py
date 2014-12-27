__author__ = 'zieghailo'
import numpy as np
from matplotlib.tri import Triangulation
from point import Point
from triangle import Triangle

class Mesh(object):

    def __init__(self, img, n):
        self.N = n
        self._points = []
        self._triangles = []
        self._img = img

    @property
    def image(self):
        return self._img

    @property
    def points(self):
        return self._points

    @property
    def triangles(self):
        return self._triangles

    def _randomize(self):
        # TODO maybe we need to reverse height and width?
        h, w = self.image.shape[:2]

        for i in range(self.N - 4):
            self.points.append(Point(h, w))

        self.points.append(Point(x=0, y=0))
        self.points.append(Point(x=w, y=0))
        self.points.append(Point(x=0, y=h))
        self.points.append(Point(x=w, y=h))

    def remove_point(self, index):
        del(self.points[index])

    def add_point(self, new_point):
        self.points.append(new_point)

    def triangulate(self):
        x = list(p.x for p in self.points)
        y = list(p.y for p in self.points)

        self._triangulation = Triangulation(x, y)

        for t in self._triangulation.triangles:
            triangle = self._find_triangle_with_points(t)
            if triangle is None:
                self.triangles.append(Triangle(set(t)))

    def _find_triangle_with_points(self, point_list):
        """
        Goes through the list of triangles, and compares
        their vertices to the three points given by the point_list
        :param point_list: indices of three points defining a triangle
        :return: The triangle specified by the point_list if it exists. Otherwise returns None.
        """
        point_set = set(self.points[point_list])

        for triangle in self.triangles:
            if triangle.vertices == point_set:
                return triangle

        return None



