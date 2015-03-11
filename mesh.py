__author__ = 'zieghailo'

import numpy as np
from random import choice
from heapq import nsmallest, nlargest

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

    @staticmethod
    def sort_by_neighbors(points):
        """
        In order to assign the triangles to the right neighborhoods in linear time,
        we need to follow through each points neighbors, and create a list of lists
        pointing back.
        :param points: list of points from the mesh
        :return: list of points pointing to this point
        """
        # nb_list = [set()] * len(points)  # the neighbor list to be returned
        nb_list = [set() for _ in enumerate(points)]
        for i, p in enumerate(points):
            for n in p.neighbors:
                nb_list[n].add(i)
        return nb_list

    @profile
    def evolve(self, temp, absolute_error=False, parallel=True):
        """
        Moves the points around randomly, keeping the changes that reduce errors,
        and reverting those that don't. Each evolve cycle the whole image is retruangulated
        and repainted twice.
        :param temp: The temperature of the simulated annealing, representing max pixel jump.
        :param parallel: Bool specifying if the colorization should be parallel.
        """
        # create a control triangulation, calculate the colors and the errors
        old_triangulation = Triangulation(self.points)
        self._triangulation = old_triangulation
        old_triangulation.colorize_stack(absolute_error, parallel)

        # assign neighbors to each point
        old_triangulation.assign_neighbors(self.points)

        # calculate the error of the triangulation, used for plotting purposes only
        self._error = old_triangulation.calculate_global_error()

        # self._color_triangles_with_verts(self.points[100].neighbors)

        # move the points around, distance depending on the annealing temperature
        for point in self.points:
            point.shift(temp)

        # calculate the new triangulation, colors and errors
        new_triangulation = Triangulation(self.points)
        new_triangulation.colorize_stack(absolute_error, parallel)

        # add the new neighbors to the old ones
        new_triangulation.assign_neighbors(self.points)

        # list of lists, each element i consists of points who have the neighbor point[i]
        nb_list = self.sort_by_neighbors(self.points)

        old_errors = old_triangulation.neighborhood_errors(self.points, nb_list)
        new_errors = new_triangulation.neighborhood_errors(self.points, nb_list)

        for i, p in enumerate(self.points):
            p.neighbors = set()
            if old_errors[i] > new_errors[i]:
                p.accept()
            else:
                p.reset()

    @profile
    def slow_purge(self, n=10):
        """
        Purges the n worst points and triangles in the triangulation.
        :param n: Number of points/triangles to be purged
        """
        point_errors = self._triangulation.calculate_point_errors(self.points)
        npoint_indices = nsmallest(n, enumerate(point_errors[4:]), lambda x: x[1])
        npoint_indices = [x[0] for x in npoint_indices]
        # we cannot just go through the list and delete points, as it will mess with the remaining points
        for pi in sorted(npoint_indices, reverse=True):
            self.remove_point(self.points[pi + 4])  # 4 is used to jump over the first fixed points

        triangle_errors = self._triangulation.calculate_triangle_errors()
        ntriangle_indices = nlargest(n, enumerate(triangle_errors), lambda x: x[1])
        for ti in ntriangle_indices:
            self.split_triangle(self._triangulation._triangles[ti[0]])

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

