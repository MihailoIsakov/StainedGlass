#! /usr/bin/env python

__author__ = 'zieghailo'
import numpy as np
from matplotlib.tri import Triangulation
from multiprocessing import Pool
import functools
from time import time
from collections import deque

from point import Point
from meshcollection import FlatMeshCollection
from trimath import triangle_sum
from support.lru_cache import LRUCache
from support.numpy_hash import hashable

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

        # TODO maybe implement it as a linked list so that removing points from the middle and appending is faster?
        self._points = []
        self._triangles = deque()

        self._triangle_stack = deque()
        self._triangle_cache = LRUCache(8192)

        self._triangulation = None
        self._randomize()

    def _randomize(self):
        # TODO maybe we need to reverse height and width?
        h, w = self.image.shape[:2]

        for i in range(self.N - 4):
            self.points.append(Point(w, h))

        self.points.append(Point(w, h, x=0, y=0))
        self.points.append(Point(w, h, x=w, y=0))
        self.points.append(Point(w, h, x=0, y=h))
        self.points.append(Point(w, h, x=w, y=h))

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
    def error(self):
        return sum(tr.error for tr in self.triangles)

    @property
    def colors(self):
        # TODO can be optimized to check if the current version is still consistent
        return [t.color for t in self.triangles]

    @property
    def triangle_errors(self):
        return [t.error for t in self.triangles]

    @property
    def point_errors(self):
        return [p.error for p in self.points]
    #endregion

    def remove_point(self, point):
        self.points.remove(point)

    def remove_point_at(self, index):
        self.points.pop(index)

    def add_point(self, new_point):
        self.points.append(new_point)

    def split_triangle(self, triangle):
        """
        Creates a point inside the triangle, thereby splitting it.
        :param triangle: 3x2 numpy array, each collumn is a
        :return: the created point
        """
        p1 = triangle.flat_vertices[:, 0]
        p2 = triangle.flat_vertices[:, 1]
        p3 = triangle.flat_vertices[:, 2]
        p2 = p2 - p1
        p3 = p3 - p1

        while True:
            s = np.random.rand()
            t = np.random.rand()
            if s + t <= 1:
                break

        new_point = p1 + p2 * s + p3 * t
        point = Point(x=new_point[0], y=new_point[1])
        self.add_point(point)
        return point

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

    def get_color(self, triangle):
        result = self.process_triangle(triangle)
        if result is None:
            raise KeyError("The triangle was not previously colorized.")
        return result[0]

    def process_triangle(self, triangle):
        """
        Lookup the color/error of the triangle. If the result has already been calculated,
        return it. Otherwise, add it to the triangle stack and return None.
        :param triangle: 2x3 numpy array of the triangles coordinates.
        :return: color and error tuple if the result was calculated before, otherwise None.
        """
        hashed = hashable(triangle)
        try:
            result = self._triangle_cache.get(hashed)
        except KeyError:
            self._triangle_stack.append(triangle)
            result = None
        return result

    def delaunay(self):
        """
        Triangulate the current points, salvage results from the cache,
        add missing results to the stack.
        """
        x = np.array([p.x for p in self.points])
        y = np.array([p.y for p in self.points])
        self._triangles = deque()

        while True:
            try:
                self._triangulation = Triangulation(x, y)
            except Exception:
                print("Triangulation failed, repeating.")
                print x
                continue
            break

        # goes through the triangles and sifts the new ones out, throws them on the stack
        for i, t in enumerate(self._triangulation.triangles):
            triangle = self.get_triangle(t)
            self._triangles.append(triangle)
            self.process_triangle(triangle)

    def evolve(self, maxerr = 1000, minerr=1000):
        # TODO somethings really fishy here
        for p in self.points:
            if p.error < minerr:
                self.remove_point(p)

        self.delaunay()
        self.colorize_stack(parallel=False)
        #
        # for tr in self.triangles:
        #     if tr.error > maxerr:
        #         self.split_triangle(tr)
        # for p in self.points:
        #     p.move(delta=1)

        self.delaunay()
        self.colorize_stack(parallel=False)

    def colorize_stack(self, parallel=False):
        if not parallel:
            while len(self._triangle_stack) > 0:
                triangle = self._triangle_stack.pop()
                result = triangle_sum(self.image, triangle)
                self._triangle_cache.set(hashable(triangle), result)
        else:
            raise NotImplementedError
            # f = functools.partial(triangle_sum, self.image)
            #
            # stack_vertices = [t.flat_vertices for t in self._triangle_stack]
            #
            # pool = Pool()
            # result = map(f, stack_vertices)
            # pool.close()
            # pool.join()
            #
            # for i, tr in enumerate(self._triangle_stack):
            #     self._triangle_stack[i]._color = result[i][0]
            #     self._triangle_stack[i]._error = result[i][1]

def main():
    print("Running mesh.py")

    global mesh
    import cv2
    img = cv2.imread('images/lion.jpg')
    img = np.flipud(img)

    mesh = Mesh(img, 1000)
    print "Triangulating."
    mesh.delaunay()
    print "Coloring."
    mesh.colorize_stack()

    import plotter
    col = FlatMeshCollection(mesh)
    ax = plotter.start()
    ax = plotter.plot_mesh_collection(col, ax)

    past = time()
    now = 0
    for i in range(100000):
        mesh.evolve()

        if i % 1 == 0:
            now = time()
            print(now - past)
            past = now

            col = FlatMeshCollection(mesh)
            ax = plotter.plot_mesh_collection(col, ax)


    plotter.keep_plot_open()

if __name__ == "__main__":
    main()




