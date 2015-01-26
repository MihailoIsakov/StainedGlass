__author__ = 'zieghailo'
import numpy as np
from collections import deque

from point import Point as BasePoint
from SApoint import SApoint as Point
from trimath import triangle_sum, triangle_sum_sw, rand_point_in_triangle, DelaunayXY
from support.lru_cache import LRUCache

# multiprocessing approach
from multiprocessing import Pool
from random import sample
from heapq import nlargest, nsmallest

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

    def __init__(self, img, n):
        self.N = n
        self._img = img
        BasePoint.set_borders(img.shape[1], img.shape[0]) # for some reason shape gives us y, then x

        # TODO maybe implement it as a linked list so that
        # removing points from the middle and appending is faster?
        self._points = []
        self._triangles = deque()

        self._triangle_stack = deque()
        self._CACHE_SIZE = 65536
        self._triangle_cache = LRUCache(self._CACHE_SIZE)

        self._triangulation = None
        self._randomize()

        print("Starting triangulation.")
        self.delaunay()
        print("Colorizing stack")
        self.colorize_stack()
        self.update_errors()

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

    @property
    def triangles(self):
        return self._triangles

    @property
    def colors(self):
        # TODO can be optimized to check if the current version is still consistent
        return [t.color for t in self.triangles]

    @property
    def point_errors(self):
        return [p.error for p in self.points]

    @property
    def triangle_errors(self):
        return [self.get_triangle_error(tr) for tr in self.triangles]

    @property
    def error(self):
        err = np.sum(self.get_triangle_error(tr) for tr in self.triangles)
        return err
    #endregion

    def remove_point(self, point):
        if not point._fixed:
            self.points.remove(point)

    def add_point(self, new_point):
        self.points.append(new_point)

    def split_triangle(self, triangle):
        """
        Creates a point inside the triangle, thereby splitting it.
        :param triangle: 3x2 numpy array, each collumn is a
        :return: the created point
        """
        [x, y] = rand_point_in_triangle(triangle)

        point = Point(x, y)
        self.add_point(point)
        return point

    def update_errors(self):
        for p in self.points:
            p.error = 0
        for i, tr_index in enumerate(self._triangulation.simplices):
            err = self.get_result_at(i)[1]
            for p_i in tr_index:
                self.points[p_i].error += err

    def get_triangle(self, point_indices):
        """
        Gets the coordinates of the triangle from indices of three points in self.points
        :param point_indices: indices of three points in self.points
        :return: 2x3 numpy array of triangle vertices coordinates
        """
        triangle = np.zeros([2, 3])
        triangle[:, 0] = self.points[point_indices[0]].position
        triangle[:, 1] = self.points[point_indices[1]].position
        triangle[:, 2] = self.points[point_indices[2]].position
        return triangle

    def get_result(self, triangle):
        try:
            result = self._triangle_cache.get(triangle)
        except KeyError:
            return ((0, 1, 0), 0)
            raise KeyError("The triangle was not previously colorized.")
        return result

    def get_result_at(self, triangle_index):
        triangle = self.triangles[triangle_index]
        return self.get_result(triangle)

    def get_triangle_color(self, triangle):
        return self.get_result(triangle)[0]

    def get_triangle_error(self, triangle):
        return self.get_result(triangle)[1]

    def process_triangle(self, triangle):
        """
        Lookup the color/error of the triangle. If the result has already been calculated,
        return it. Otherwise, add it to the triangle stack and return None.
        :param triangle: 2x3 numpy array of the triangles coordinates.
        :return: color and error tuple if the result was calculated before, otherwise None.
        """
        try:
            result = self._triangle_cache.get(triangle)
        except KeyError:
            self._triangle_stack.append(triangle)
            result = None
        return result

    def delaunay(self):
        """
        Triangulate the current points,
        add the triangle numpy arrays to self.triangles,
        salvage results from the cache,
        add missing results to the stack.
        """
        x = np.array([p.x for p in self.points])
        y = np.array([p.y for p in self.points])
        self._triangles = deque()

        try:
            self._triangulation = DelaunayXY(x, y)
        except Exception:
            pass

        if len(self._triangulation.simplices) > self._CACHE_SIZE:
            raise MemoryError("Cache is not smaller than the number of triangles in the mesh.")

        # goes through the triangles and sifts the new ones out, throws them on the stack
        for i, t in enumerate(self._triangulation.simplices):
            triangle = self.get_triangle(t)
            self._triangles.append(triangle)
            self.process_triangle(triangle)

    def triangulate(self, parallel=True):
        self.delaunay()
        self.colorize_stack(parallel)
        self.update_errors()

    @profile
    def evolve(self, temp, purge=False, maxerr=2000, minerr=500, parallel=True):
        for p in self.points:
            p.shift(temp)

        self.triangulate()

        for p in self.points:
            p.evaluate()

        if purge:
            self.ordered_purge(0.1, maxerr, minerr)

    def random_purge(self, sample_percentage, chance, maxerr, minerr):
        self.triangulate()

        sample_size = int(len(self.points) * sample_percentage)
        for p in sample(self.points, sample_size):
            if p.error < minerr:
                if np.random.rand() < chance:
                    self.remove_point(p)

        sample_size = int(len(self.triangles) * sample_percentage)
        for tr in sample(self.triangles, sample_size):
            if self.get_triangle_error(tr) > maxerr:
                if np.random.rand() < chance:
                    self.split_triangle(tr)

    def ordered_purge(self, decimate_percentage, maxerr, minerr):
        self.triangulate()

        point_dec = int(len(self.points) * decimate_percentage)
        triang_dec = int(len(self.triangles) * decimate_percentage)

        smallest = nsmallest(point_dec, self.points, lambda x: x.error)
        for point in smallest:
            if point.error > minerr:
                break  # in case even the worst points are within range, quit
            self.remove_point(point)

        largest = nlargest(triang_dec, self.triangles, lambda x: self.get_triangle_error(x))
        for triangle in largest:
            if self.get_triangle_error(triangle) < maxerr:
                break  # in case even the worst triangles are within range, quit
            self.split_triangle(triangle)

        self.triangulate()

    @profile
    def colorize_stack(self, parallel=True):
        if not parallel:
            while len(self._triangle_stack) > 0:
                triangle = self._triangle_stack.pop()
                result = triangle_sum(triangle)
                self._triangle_cache.set(triangle, result)
            if len(self._triangle_stack) != 0:
                raise AssertionError("Stack not fully colored")
        else:
            pool = Pool(processes=8)
            triangles = list(self._triangle_stack)
            results = pool.map(triangle_sum, triangles)

            pool.close()
            pool.join()

            for triangle, res in zip(self._triangle_stack, results):
                self._triangle_cache.set(triangle, res)

            self._triangle_stack.clear()

    def is_consistent(self):
        cons = True
        for tr in self.triangles:
            try:
                res = self._triangle_cache.get(tr)
            except KeyError:
                cons = False

        return cons



