__author__ = 'zieghailo'

import unittest
import numpy.testing as nptest
from trimath import *

class MyTestCase(unittest.TestCase):

    def test_cv2_triangle_sum(self):
        #chessboard
        img = np.ones([1000, 1000, 3])
        for x in range(1000):
            for y in range(1000):
                for z in range(3):
                    img[x,y,z] = (x + y) % 2

        img *= 255

        tr = np.array([[100, 200, 300], [300, 100, 200]])

        from trimath import cv2_triangle_sum
        import numpy.testing as nptest

        res = cv2_triangle_sum(img, tr)
        color = res[0]
        error = res[1]
        nptest.assert_allclose(color[0], 0.5, atol=0.01)
        nptest.assert_allclose(color[1], 0.5, atol=0.01)
        nptest.assert_allclose(color[2], 0.5, atol=0.01)



if __name__ == '__main__':
    unittest.main()
