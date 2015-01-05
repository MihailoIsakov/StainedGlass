#! /usr/bin/env python

__author__ = 'zieghailo'
import numpy as np
from matplotlib.tri import Triangulation
from multiprocessing import Pool
import functools
from time import time

from point import Point
from triangle import Triangle
from meshcollection import MeshCollection
from trimath import triangle_sum

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

        self._points = []
        self._triangles = []
        self._triangle_stack = []

        self._triangulation = None
        self._randomize()

    def _randomize(self):
        # TODO maybe we need to reverse height and width?
        h, w = self.image.shape[:2]

        for i in range(self.N - 4):
            self.points.append(Point(max_x=w, max_y=h))

        self.points.append(Point(x=0, y=0))
        self.points.append(Point(x=w, y=0))
        self.points.append(Point(x=0, y=h))
        self.points.append(Point(x=w, y=h))

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

    def create_triangle(self, vertices):
        tr = Triangle(self, vertices)
        tr.used = True
        self.triangles.append(tr)
        self._triangle_stack.append(tr)

    def remove_triangle(self, triangle):
        triangle.delete()
        try:
            self.triangles.remove(triangle)
        except ValueError:
            print("ValueError: removing nonexistent triangle")
            pass

    @profile
    def delaunay(self):
        x = [p.x for p in self.points]
        y = [p.y for p in self.points]
        for t in self.triangles: t.used = False

        while True:
            try:
                self._triangulation = Triangulation(x, y)
            except Exception:
                pass
            break

        self._triangle_stack = []

        for i, t in enumerate(self._triangulation.triangles):
            triangle = self._triangle_exists(t)

            if triangle is not None:
                triangle.used = True  # this is how we know not to discard the triangle
            else:
                vertices = [self.points[l] for l in t]
                self.create_triangle(vertices)

        for tr in self.triangles:
            if not tr.used:
                self.remove_triangle(tr)

    def _triangle_exists(self, point_list):
        """
        Goes through the list of triangles, and compares
        their vertices to the three points given by the point_list
        :param point_list: indices of three points defining a triangle
        :return: The triangle specified by the point_list if it exists, and its index. Otherwise returns None.
        """
        points = self.points
        result = \
            points[point_list[0]].triangles & \
            points[point_list[1]].triangles & \
            points[point_list[2]].triangles

        # will return True if the set isn't empty
        try:
            triangle = result.pop()
        except KeyError:
            triangle = None
        return triangle

    @profile
    def evolve(self, maxerr = 1000, minerr=500):
        # TODO somethings really fishy here
        # for p in self.points:
        #     if p.error < minerr:
        #         self.remove_point(p)
        #
        # self.delaunay()
        # self.colorize_stack(parallel=False)
        #
        # for tr in self.triangles:
        #     if tr.error > maxerr:
        #         self.split_triangle(tr)
        for p in self.points:
            p.move()

        self.delaunay()
        self.colorize_stack(parallel=False)

    def colorize_stack(self, parallel=True):
        if parallel:
            f = functools.partial(triangle_sum, self.image)

            stack_vertices = [t.flat_vertices for t in self._triangle_stack]

            pool = Pool()
            result = map(f, stack_vertices)
            pool.close()
            pool.join()

            for i, tr in enumerate(self._triangle_stack):
                self._triangle_stack[i]._color = result[i][0]
                self._triangle_stack[i]._error = result[i][1]
        else:
            for t in self._triangle_stack:
                t.colorize()


def main():
    print "Running mesh.py"

    global m
    import cv2

    img = cv2.imread('images/lion.jpg')
    img = np.flipud(img)

    m = Mesh(img, 1000)
    m.delaunay()

    for tr in m.triangles:
        tr.colorize()

    import plotter
    col = MeshCollection(m.triangles, m.colors)
    ax = plotter.start()
    ax = plotter.plot_mesh_collection(col, ax)

    past = time()
    now = 0
    for i in range(100000):
        m.evolve()

        if i % 1 == 0:
            now = time()
            print now - past
            past = now

            col = MeshCollection(m.triangles, m.colors)
            ax = plotter.plot_mesh_collection(col, ax)


    plotter.keep_plot_open()

if __name__ == "__main__":
    main()




