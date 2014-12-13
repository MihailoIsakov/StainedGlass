__author__ = 'zieghailo'

import unittest
from trimath import *

class MyTestCase(unittest.TestCase):
    def test_rand_point(self):
        tr = np.array([[1, 2, 3], [3, 1, 2]])

        for i in range(1000):
            p = rand_point_in_triangle(tr)
            self.assertTrue(in_triangle(p, tr))

if __name__ == '__main__':
    unittest.main()
