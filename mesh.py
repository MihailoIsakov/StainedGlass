__author__ = 'zieghailo'

import numpy as np
from random import sample
from heapq import nlargest, nsmallest

from triangulation import *
from point import Point as BasePoint
from SApoint import SApoint as Point
from trimath import rand_point_in_triangle



# region needed so that @profile doesn't cause an error
import __builtin__

try:
    __builtin__.profile
except AttributeError:
    # No line profiler, provide a pass-through version
    def profile(func): return func
    __builtin__.profile = profile
# endregion


class Mesh(object):

    def __init__(self, img, n, parallel=True):
        self.N = n
        self._img = img
        BasePoint.set_borders(img.shape[1], img.shape[0]) # for some reason shape gives us y, then x

        self._points = []

        self._triangulation = None
        self._randomize()

        self.triangulate(parallel)

    def _randomize(self):
        self._points = []
        h, w = self.image.shape[:2]

        self.points.append(Point(0, 0, is_fixed=True))
        self.points.append(Point(w, 0, is_fixed=True))
        self.points.append(Point(0, h, is_fixed=True))
        self.points.append(Point(w, h, is_fixed=True))

        for i in range(self.N - 4):
            self.points.append(Point())

    # region properties
    @property
    def image(self):
        return self._img

    @property
    def points(self):
        return self._points

    #endregion

    def remove_point(self, point):
        if not point._fixed:
            self.points.remove(point)

    def split_triangle(self, triangle):
        """
        Creates a point inside the triangle, thereby splitting it.
        :param triangle: 3x2 numpy array, each collumn is a
        :return: the created point
        """
        [x, y] = rand_point_in_triangle(triangle)

        point = Point(x, y)
        self.points.append(point)
        return point

    def assign_neighbors(self):

        for verts in self._triangulation.simplices:
            points = [self.points[x] for x in verts]
            for p in points:
                p.neighbors.update(set(points))

    def calc_triangulation_errors(self, triangulation):
        for point in self.points:
            error = 0

            for tri_ind, simplices in enumerate(triangulation.simplices):
                included = True
                for vert in simplices:
                    if vert not in point.neighbors:
                        included = False
                        break
                if included:
                    error += self.nptriangle2result(self.points2nptriangle(simplices))[1]

    def triangulate(self, parallel=True):
        self._triangulation = Triangulation(self.points)
        self._triangulation.colorize_stack(parallel)
        self._triangulation.calculate_triangle_errors()

    @profile
    def evolve(self, temp, parallel=True):
        old_triangulation = Triangulation(self.points)
        self._triangulation = old_triangulation
        old_triangulation.colorize_stack(parallel)
        old_triangulation.assign_neighbors()

        self._error = old_triangulation.calculate_global_error()

        # self._color_triangles_with_verts(self.points[100].neighbors)

        for point in self.points:
            point.shift(temp)

        new_triangulation = Triangulation(self.points)
        new_triangulation.colorize_stack(parallel)
        new_triangulation.assign_neighbors()


        # self._color_triangles_with_verts(self.points[100].neighbors)
        for point in self.points:
            old_triangles = old_triangulation.find_triangles_with_indices(point.neighbors)
            old_error = 0
            for tr in old_triangles:
                old_error += nptriangle2error(old_triangulation.points2nptriangle(tr))

            new_triangles = new_triangulation.find_triangles_with_indices(point.neighbors)
            new_error = 0
            for tr in new_triangles:
                new_error += nptriangle2error(new_triangulation.points2nptriangle(tr))

            if new_error < old_error:
                point.accept()
            else:
                point.reset()

            point.neighbors = set()

    @profile
    def slow_purge(self):
        point_errors = self._triangulation.calculate_point_errors()
        mn = np.argmin(point_errors[4:])
        self.remove_point(self.points[mn+4])

        triangle_errors = self._triangulation.calculate_triangle_errors()
        mx = np.argmax(triangle_errors)
        self.split_triangle(self._triangulation._triangles[mx])


    def _color_triangles_with_verts(self, verts):
        from support import lru_cache as cache
        for tr in self._triangulation.delaunay.simplices:
            allin = True
            for v in tr:
                if v not in verts:
                    allin = False
            if allin:
                nptr = self._triangulation.points2nptriangle(tr)
                res = cache.get(nptr)
                cache.set(nptr, ((0, 0, 1), res[1]))

    def _color_neighbors(self, pindex):
        from support import lru_cache as cache
        for tr in self._triangulation.delaunay.simplices:
            if pindex in tr:
                nptr = self._triangulation.points2nptriangle(tr)
                res = cache.get(nptr)
                cache.set(nptr, ((1, 0, 0), res[1]))