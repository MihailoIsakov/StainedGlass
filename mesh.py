#! /usr/bin/env python

__author__ = 'zieghailo'
import numpy as np
from matplotlib.tri import Triangulation
from multiprocessing import Process
from time import clock

from point import Point
from triangle import Triangle
from meshcollection import MeshCollection


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
        self.add_point(Point(x=new_point[0], y=new_point[1]))
        # self.remove_triangle(triangle)

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

    def delaunay(self):
        x = [p.x for p in self.points]
        y = [p.y for p in self.points]
        for t in self.triangles: t.used = False

        self._triangulation = Triangulation(x, y)
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
        point_set = set(point_list)
        points = [self.points[i] for i in point_list]

        result = points[0].triangles
        for p in points:
            result = result & p.triangles
        # will return True if the set isn't empty
        try:
            triangle = result.pop()
        except KeyError:
            triangle = None
        return triangle

    def evolve(self):
        # TODO somethings really fishy here
        minerr = np.argmin(self.point_errors)
        self.remove_point_at(minerr)
        maxerr = np.argmax(self.triangle_errors)
        self.split_triangle(self.triangles[maxerr])

        self.delaunay()

        jobs = []
        for tr in self._triangle_stack:
            print("jobs: ",len(self._triangle_stack))
            p = Process(target=tr.colorize)
            jobs.append(p)
            p.start()

        for job in jobs:
            job.join()

        for tr in self._triangle_stack:
            print tr.color

        # # print("stack length", len(self._triangle_stack))
        # while len(self._triangle_stack) > 0:
        #     triangle = self._triangle_stack.pop()
        #
        #     triangle.colorize()

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

    past = 0
    now = 0
    for i in range(100000):
        m.evolve()

        if i % 100 == 0:
            past = now
            now = clock()
            print now - past
            for i, t in enumerate(m.triangles):
                if t._color is None:
                    t._color = (0,0,0)
                    print i
            col = MeshCollection(m.triangles, m.colors)
            ax = plotter.plot_mesh_collection(col, ax)


    plotter.keep_plot_open()

if __name__ == "__main__":
    main()




