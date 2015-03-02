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
            # print error

    def triangulate(self, parallel=True):
        self._triangulation = Triangulation(self.points)
        self._triangulation.colorize_stack(parallel)
        self._triangulation.calculate_triangle_errors()

    @staticmethod
    def sort_by_neighbors(points):
        """
        In order to assign the triangles to the right neighborhoods in linear time,
        we need to follow through each points neighbors, and create a list of lists
        pointing back.
        :param points: list of points from the mesh
        :return: list of points pointing to this point
        """
        nb_list = [[]] * len(points)  # the neighbor list to be returned
        for i, p in enumerate(points):
            for n in p.neighbors:
                nb_list[i].append(n)
        return nb_list

    @profile
    def evolve(self, temp, purge=False, parallel=True):
        """
        Moves the points around randomly, keeping the changes that reduce errors,
        and reverting those that don't. Each evolve cycle the whole image is retruangulated
        and repainted twice.
        :param temp: The temperature of the simulated annealing, representing max pixel jump.
        :param purge: Bool specifying if any points should be added and removed this turn.
        :param parallel: Bool specifying if the colorization should be parallel.
        """
        # create a control triangulation, calculate the colors and the errors
        old_triangulation = Triangulation(self.points)
        self._triangulation = old_triangulation
        old_triangulation.colorize_stack(parallel)

        # assign neighbors to each point
        old_triangulation.assign_neighbors()

        # calculate the error of the triangulation, used for plotting purposes only
        self._error = old_triangulation.calculate_global_error()

        # move the points around, distance depending on the annealing temperature
        for point in self.points:
            point.shift(temp)

        # calculate the new triangulation, colors and errors
        new_triangulation = Triangulation(self.points)
        new_triangulation.colorize_stack(parallel)

        # add the new neighbors to the old ones
        new_triangulation.assign_neighbors()

        nb_list = self.sort_by_neighbors(self.points)

        old_triangulation.assign_errors(nb_list)
        old_errors = [p.error for p in self.points]

        new_triangulation.assign_errors(nb_list)
        new_errors = [p.error for p in self.points]

        for i, p in enumerate(self.points):
            if old_errors[i] > new_errors[i]:
                p.accept()
            else:
                p.reset()

            p.neighbors = set()

        # # simulated annealing magic. Find which points to reset, and which to keep as they are.
        # for point in self.points:
        #     old_triangles = old_triangulation.find_triangles_with_indices(point.neighbors)
        #     old_error = 0
        #     for tr in old_triangles:
        #         old_error += nptriangle2error(old_triangulation.points2nptriangle(tr))
        #
        #     new_triangles = new_triangulation.find_triangles_with_indices(point.neighbors)
        #     new_error = 0
        #     for tr in new_triangles:
        #         new_error += nptriangle2error(new_triangulation.points2nptriangle(tr))
        #
        #     if new_error < old_error:
        #         point.accept()
        #     else:
        #         point.reset()
        #
        #     point.neighbors = set()

        if purge:
            self.slow_purge()

    @profile
    def slow_purge(self):
        point_errors = self._triangulation.calculate_point_errors()
        mn = np.argmin(point_errors[4:])
        self.remove_point(self.points[mn+4])

        triangle_errors = self._triangulation.calculate_triangle_errors()
        mx = np.argmax(triangle_errors)
        self.split_triangle(self._triangulation._triangles[mx])