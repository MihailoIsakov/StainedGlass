__author__ = 'zieghailo'
import numpy as np
from matplotlib.tri import Triangulation
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from point import Point
from triangle import Triangle
from meshcollection import MeshCollection

class Mesh(object):

    def __init__(self, img, n):
        self.N = n
        self._points = []
        self._triangles = []
        self._img = img
        self._triangulation = None

        self._randomize()

    @property
    def image(self):
        return self._img

    @property
    def points(self):
        return self._points

    @property
    def triangles(self):
        return self._triangles

    @property
    def colors(self):
        return [t.color for t in self.triangles]

    def _randomize(self):
        # TODO maybe we need to reverse height and width?
        h, w = self.image.shape[:2]

        for i in range(self.N - 4):
            self.points.append(Point(max_x=w, max_y=h))

        self.points.append(Point(x=0, y=0))
        self.points.append(Point(x=w, y=0))
        self.points.append(Point(x=0, y=h))
        self.points.append(Point(x=w, y=h))

    def remove_point(self, index):
        del(self.points[index])

    def add_point(self, new_point):
        self.points.append(new_point)

    def delaunay(self):
        x = list(p.x for p in self.points)
        y = list(p.y for p in self.points)

        self._triangulation = Triangulation(x, y)

        for t in self._triangulation.triangles:
            triangle = self._find_triangle(t)
            vertices = [self.points[l] for l in t]

            if triangle is None:
                self.triangles.append(Triangle(vertices))

    def _find_triangle(self, point_list):
        """
        Goes through the list of triangles, and compares
        their vertices to the three points given by the point_list
        :param point_list: indices of three points defining a triangle
        :return: The triangle specified by the point_list if it exists. Otherwise returns None.
        """
        point_set = set(point_list)

        for triangle in self.triangles:
            if triangle.vertices == point_set:
                return triangle

        return None


def main():
    print "Running mesh.py"

    global m
    import cv2

    img = cv2.imread('images/lion.jpg')
    m = Mesh(img, 100)
    m.delaunay()

    for tr in m.triangles:
        tr.colorize(m.image)
        print tr.color

    import plotter
    col = MeshCollection(m.triangles, m.colors)
    ax = plotter.start()
    ax = plotter.plot_mesh_collection(col, ax)

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()




