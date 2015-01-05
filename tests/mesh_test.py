__author__ = 'zieghailo'

import unittest
import trimath
from mesh import Mesh
from point import Point


class MeshTest(unittest.TestCase):
    def setUp(self):
        import cv2
        img = cv2.imread('../images/lion.jpg')
        self.N = 100
        self.mesh = Mesh(img, self.N)

    def test_remove_point(self):
        mesh = self.mesh
        p = mesh.points[50]

        self.assertTrue(p in mesh.points)
        mesh.remove_point(p)
        self.assertTrue(p not in mesh.points)
        self.assertEquals(len(mesh.points), self.N - 1)

    def test_remove_point_at(self):
        mesh = self.mesh
        k = 50
        p = mesh.points[k]

        point_num = len(mesh.points)
        self.assertIn(p, mesh.points)
        mesh.remove_point_at(k)
        self.assertNotIn(p, mesh.points)

        self.assertEquals(len(mesh.points), point_num - 1)

    def test_add_point(self):
        new_p = Point(100, 100)
        point_num = len(self.mesh.points)

        self.mesh.add_point(new_p)
        self.assertIn(new_p, self.mesh.points)
        self.assertEquals(len(self.mesh.points), point_num + 1)

    def test_split_triangle(self):
        mesh = self.mesh
        triangle = mesh.triangles[50]
        pnum = len(mesh.points)
        tnum = len(mesh.triangles)

        mesh.split_triangle(triangle)
        trimath.in_triangle()


if __name__ == '__main__':
    unittest.main()
