__author__ = 'zieghailo'

import unittest
from point import Point
from triangle import Triangle

class PointTest(unittest.TestCase):

    def setUp(self):
        self.p1 = Point(x=10, y=20)
        self.p2 = Point(x=40, y=50)
        self.p3 = Point(x=80, y=15)
        self.p4 = Point(x=30, y=21)

        self.t1 = Triangle(None, [self.p1, self.p2, self.p3])
        self.t2 = Triangle(None, [self.p1, self.p2, self.p4])
        self.t1._error = 100
        self.t2._error = 50

    def test_flat_vertices(self):
        self.assertEquals(self.p1.x, self.t1.flat_vertices[0, 0])
        self.assertEquals(self.p1.y, self.t1.flat_vertices[1, 0])
        self.assertEquals(self.p2.x, self.t1.flat_vertices[0, 1])
        self.assertEquals(self.p2.y, self.t1.flat_vertices[1, 1])
        self.assertEquals(self.p3.x, self.t1.flat_vertices[0, 2])
        self.assertEquals(self.p3.y, self.t1.flat_vertices[1, 2])

    def test_add_triangle(self):
        # the points triangle is added when it is created
        self.assertEquals(self.p3.triangles.pop(), self.t1)

    def test_remove_triangle(self):
        self.p1.remove_triangle(self.t1)
        self.assertEquals(len(self.p1.triangles), 1)
        self.p1.remove_triangle(self.t1)
        self.p1.remove_triangle(self.t2)
        self.assertEquals(len(self.p1.triangles), 0)

    def test_calc_error(self):
        self.p1._calc_error()
        self.assertEquals(self.p1.error, 150)

    def test_calc_error_add(self):
        t3 = Triangle(None, [self.p1, self.p3, self.p4])
        t3._error = 30
        self.p1._calc_error()
        self.assertEquals(self.p1.error, 180)

    def test_calc_error_remove(self):
        self.p1.remove_triangle(self.t2)
        self.p1._calc_error()
        self.assertEquals(self.p1.error, 100)

if __name__ == '__main__':
    unittest.main()
