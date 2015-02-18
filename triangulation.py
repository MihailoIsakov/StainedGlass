__author__ = 'zieghailo'

from collections import deque
import numpy as np
from multiprocessing import Pool

from trimath import DelaunayXY, cv2_triangle_sum
from support import lru_cache as cache

__all__ = ['nptriangle2result', 'nptriangle2color', 'nptriangle2error', 'Triangulation']


def nptriangle2result(triangle):
    try:
        result = cache.get(triangle)
    except KeyError:
        return ((0, 1, 0), 0)
        raise KeyError("The triangle was not previously colorized.")
    return result


def nptriangle2color(triangle):
    return nptriangle2result(triangle)[0]


def nptriangle2error(triangle):
    return nptriangle2result(triangle)[1]


class Triangulation():
    """
    Triangulation takes a list of points and creates a mesh,
    paints the triangles, and calculates their errors.
    For each change in the points list, a new triangulation
    is created, with its own colors and errors.
    """

    def __init__(self, points):
        """
        Triangulate the current points,
        add the triangle numpy arrays to self.triangles,
        salvage results from the cache,
        add missing results to the stack.
        """
        self.points = points
        x = np.array([p.x for p in points])
        y = np.array([p.y for p in points])

        self._triangles = deque()
        self._triangle_stack = deque()

        try:
            self.delaunay = DelaunayXY(x, y)
        except RuntimeError("Triangulation failed."):
            pass

        if len(self.delaunay.simplices) > cache.CAPACITY:
            raise MemoryError("Cache is smaller than the number of triangles in the mesh.")

        # goes through the triangles and sifts the new ones out, throws them on the stack
        for i, t in enumerate(self.delaunay.simplices):
            triangle = self.points2nptriangle(t)
            self._triangles.append(triangle)
            self.process_triangle(triangle)

    @property
    def triangles(self):
        return self._triangles

    def process_triangle(self, nptriangle):
        """
        Lookup the color/error of the triangle. If the result has already been calculated,
        return it. Otherwise, add it to the triangle stack and return None.
        :param nptriangle: 2x3 numpy array of the triangles coordinates.
        :return: color and error tuple if the result was calculated before, otherwise None.
        """
        try:
            result = cache.get(nptriangle)
        except KeyError:
            self._triangle_stack.append(nptriangle)
            result = None
        return result

    def colorize_stack(self, parallel=True):
        if not parallel:
            while len(self._triangle_stack) > 0:
                triangle = self._triangle_stack.pop()

                # triangle sum should have image as a global variable
                result = cv2_triangle_sum(triangle)

                cache.set(triangle, result)
            if len(self._triangle_stack) != 0:
                raise AssertionError("Stack not fully colored")
        else:
            pool = Pool(processes=8)
            triangles = list(self._triangle_stack)
            results = pool.map(cv2_triangle_sum, triangles)
            pool.close()
            pool.join()

            for triangle, res in zip(self._triangle_stack, results):
                cache.set(triangle, res)

            self._triangle_stack.clear()

    def assign_neighbors(self):
        for verts in self.delaunay.simplices:
            points = [self.points[x] for x in verts]
            for p in points:
                p.neighbors.update(set(verts))

    def find_triangles_with_indices(self, neighbors):
        """
        Finds all the triangles in self.delaunay
        with indices in neighbors.
        :param neighbors: The indices of points
        :return: triangles with indices in neighbors
        """
        triangles = []
        for tr in self.delaunay.simplices:
            is_in = np.array([el in neighbors for el in tr]).all()
            if is_in:
                triangles.append(tr)
        return triangles

    def calculate_errors(self, assign_errors=False):
        errors = np.zeros(len(self._triangles))

        for i, tr_index in enumerate(self.delaunay.simplices):
            err = self.trindex2result(i)[1]
            for p_i in tr_index:
                errors[p_i] += err

        if assign_errors:
            for i in range(len(self.points)):
                self.points[i].error = errors[i]

        return errors

    def calculate_global_error(self):
        error = 0

        for trind in self.delaunay.simplices:
            error += nptriangle2error(self.points2nptriangle(trind))

        return error

    def points2nptriangle(self, point_indices):
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

    def trindex2result(self, triangle_index):
        triangle = self._triangles[triangle_index]
        return nptriangle2result(triangle)