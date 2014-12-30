__author__ = 'zieghailo'

import unittest
from triangle import Triangle
from point import Point


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.p1 = Point(x=10, y=20)
        self.p2 = Point(x=40, y=50)
        self.p3 = Point(x=80, y=15)
        self.p4 = Point(x=30, y=21)

        self.t1 = Triangle(None, [self.p1, self.p2, self.p3])
        self.t2 = Triangle(None, [self.p1, self.p2, self.p4])
        self.t1._error = 100
        self.t2._error = 50

    def test_delete(self):
        self.assertTrue(self.t1 in self.p1.triangles)
        self.assertTrue(self.t1 in self.p2.triangles)
        self.assertTrue(self.t1 in self.p3.triangles)

        self.t1.delete()

        self.assertTrue(self.t1 not in self.p1.triangles)
        self.assertTrue(self.t1 not in self.p2.triangles)
        self.assertTrue(self.t1 not in self.p3.triangles)

    def test_init(self):
        t3 = Triangle(None, [self.p2, self.p3, self.p4])
        self.assertTrue(t3 in self.p2.triangles)
        self.assertTrue(t3 in self.p3.triangles)
        self.assertTrue(t3 in self.p4.triangles)

if __name__ == '__main__':
    unittest.main()
