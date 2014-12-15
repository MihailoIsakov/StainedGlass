__author__ = 'zieghailo'

import unittest
from trianglemesh import *
import numpy as np
import numpy.testing as nptest

class MeshTestCase(unittest.TestCase):
    # mesh = None
    img = None
    def setUp(self):
        import cv2
        self.img = cv2.imread("../images/tara.jpg")
        self.N = 100
        self.mesh = TriangleMesh(self.img, self.N)

    def test_sort_ascending(self):
        srtd = TriangleMesh._get_ascending_order(self.mesh.triangles)

        for row in srtd:
            self.assertLessEqual(row[0], row[1])
            self.assertLessEqual(row[1], row[2])

        column = srtd[:, 0]
        sc = np.sort(column)
        nptest.assert_array_equal(column, sc)

    def test_bigger(self):
        t1 = [10, 20, 30]
        t2 = [10, 20, 40]
        t3 = [10, 25, 10]
        t4 = [ 5, 40, 50]
        t5 = [15, 10, 20]

        self.assertTrue(TriangleMesh._bigger(t2, t1))
        self.assertTrue(TriangleMesh._bigger(t3, t1))
        self.assertTrue(TriangleMesh._bigger(t3, t2))
        self.assertTrue(TriangleMesh._bigger(t1, t4))
        self.assertTrue(TriangleMesh._bigger(t5, t1))

    def test_map_triangles(self):
        mesh1 = TriangleMesh(self.img, 100)
        tr1 = TriangleMesh._get_ascending_order(mesh1.triangles)

        kill = 40
        mesh1._remove_point(kill)
        tr2 = np.copy(mesh1.triangles)
        tr2 = TriangleMesh._get_ascending_order(tr2)
        tr2[tr2 >= kill] += 1
        tr2 = TriangleMesh._get_ascending_order(tr2)
        mapping = TriangleMesh._map_triangles(tr1, tr2)

        for i, m in enumerate(mapping):
            if not np.isnan(m):
                print i, m
                nptest.assert_array_equal(tr1[m], tr2[i])

    def test_kill_point(self):
        # FIXME: mapping returns all NaNs
        mesh = TriangleMesh(self.img, 100)
        mesh.colorize(False)
        old_tr, old_clr = TriangleMesh._get_ascending_order(mesh.triangles, mesh.colors)

        kill = 50
        mesh.kill_point(kill)
        new_tr = TriangleMesh._get_ascending_order(mesh.triangles)
        new_tr[new_tr >= kill] == 1

        mapping = TriangleMesh._map_triangles(old_tr, new_tr)

        for i, m in enumerate(mapping):
            if not np.isnan(m):
                oclr = old_clr[m]
                nclr = mesh.colors[i]
                nptest.assert_array_equal(oclr, nclr)

if __name__ == '__main__':
    unittest.main()