__author__ = 'zieghailo'

import unittest
import trimath
from numpy import testing
from mesh import Mesh
from point import Point


class MeshTest(unittest.TestCase):
    def setUp(self):
        import cv2
        img = cv2.imread('../images/lion.jpg')
        self.N = 60
        self.mesh = Mesh(img, self.N)
        self.mesh.delaunay()

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

        # TODO parametrize test case
        triangle = mesh.triangles[-1]

        mesh.split_triangle(triangle)
        self.assertTrue(trimath.in_triangle(mesh.points[-1]._position, triangle))

    def test_get_existing_result(self):
        mesh = self.mesh
        self.fake_colorize()
        c = mesh.get_result(mesh.triangles[-1])
        testing.assert_array_equal(c, mesh.triangles[-1])

    def test_get_nonexistent_result(self):
        mesh = self.mesh
        self.assertRaises(KeyError, mesh.get_result, mesh.triangles[-1])

    def fake_colorize(self):
        for tr in self.mesh.triangles:
            self.mesh._triangle_cache.set(tr, tr)  # this way all have custom values
        self.mesh._triangle_stack.clear()

    def test_process_existing_triangle(self):
        mesh = self.mesh
        self.fake_colorize()
        c = mesh.process_triangle(mesh.triangles[-1])
        testing.assert_array_equal(c, mesh.triangles[-1])

    def test_proces_new_triangle(self):
        mesh = self.mesh
        mesh._triangle_stack.clear()
        mesh.process_triangle(mesh.triangles[-1])
        self.assertEquals(1, len(mesh._triangle_stack))
        testing.assert_array_equal(mesh.triangles[-1], mesh._triangle_stack[0])

    def test_delaunay(self):
        mesh = self.mesh
        testing.assert_array_equal(mesh.triangles, mesh._triangle_stack)

    def test_delaunay_cache(self):
        mesh = self.mesh
        self.assertEquals(len(mesh._triangle_cache.cache), 0)

    def test_colorize(self):
        mesh = self.mesh
        mesh.colorize_stack()

        self.assertEquals(len(mesh._triangle_stack), 0)
        self.assertEquals(len(mesh._triangle_cache.cache), len(mesh.triangles))



if __name__ == '__main__':
    unittest.main()
