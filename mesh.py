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
        # TODO maybe we need to reverse height and width?
        h, w = self.image.shape[:2]

        for i in range(self.N - 4):
            self.points.append(Point())

        self.points.append(Point(0, 0, is_fixed=True))
        self.points.append(Point(w, 0, is_fixed=True))
        self.points.append(Point(0, h, is_fixed=True))
        self.points.append(Point(w, h, is_fixed=True))

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
        self._triangulation.calculate_errors(True)

    def evolve(self, temp, percentage=0.1, purge=False, maxerr=2000, minerr=500, parallel=True):
        old_triangulation = Triangulation(self.points)
        self._triangulation = old_triangulation
        old_triangulation.colorize_stack(parallel)
        old_triangulation.assign_neighbors()

        self._error = old_triangulation.calculate_global_error()

        # # take a random number of points and shift them
        # sample_points = sample(self.points, int(len(self.points) * percentage))
        # for point in sample_points:
        #     point.shift(temp)

        for point in self.points:
            point.shift(temp)

        new_triangulation = Triangulation(self.points)
        new_triangulation.colorize_stack(parallel)
        new_triangulation.assign_neighbors()

        # new_errors = new_triangulation.calculate_errors()
        # new_image_error = np.sum(new_errors)

        print len(self.points[0].neighbors)
        for point in self.points:
            old_triangles = old_triangulation.find_triangles_with_indices(point.neighbors)
            old_error = 0
            for tr in old_triangles:
                old_error += nptriangle2error(old_triangulation.points2nptriangle(tr))

            new_triangles = new_triangulation.find_triangles_with_indices(point.neighbors)
            new_error = 0
            for tr in new_triangles:
                new_error += nptriangle2error(old_triangulation.points2nptriangle(tr))

            if new_error < old_error:
                point.accept()
            else:
                point.reset()

            point.neighbors = set()

        if purge:
            self.ordered_purge(0.1, maxerr, minerr)
            self.triangulate(parallel)

    def ordered_purge(self, decimate_percentage, maxerr, minerr, chance=0.3):
        point_dec = int(len(self.points) * decimate_percentage)
        triang_dec = int(len(self.triangles) * decimate_percentage)

        smallest = nsmallest(point_dec, self.points, lambda x: x.error)
        for point in smallest:
            if point.error > minerr:
                break  # in case even the worst points are within range, quit
            if np.random.rand() < chance:
                self.remove_point(point)

        largest = nlargest(triang_dec, self.triangles, lambda x: self.get_triangle_error(x))
        for triangle in largest:
            if self.get_triangle_error(triangle) < maxerr:
                break  # in case even the worst triangles are within range, quit
            if np.random.rand() < chance:
                self.split_triangle(triangle)

    def is_consistent(self):
        cons = True
        for tr in self.triangles:
            try:
                res = self._triangle_cache.get(tr)
            except KeyError:
                cons = False

        return cons



