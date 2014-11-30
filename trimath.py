__author__ = 'zieghailo'

import numpy as np
import matplotlib.tri as tri

def in_trinagle(point, tri):
    """
    Check if point is inside the triangle
    :param point: two element numpy.array, p = [x,y]
    :param tri: 2x3 numpy.array of the triangle vertices
    :return: True if the point is in the triangle
    """
    mat = tri[:, 1:]
    mat[:,0] -= tri[:,0]
    mat[:,1] -= tri[:,0]
    p = point - tri[:,0]

    x = np.linalg.solve(mat, p)

    if 0 <= x[0] <= 1 and 0 <= x[1] <= 1 and x[0] + x[1] <= 1:
        return True
    return False


def color_sum(img, tri):
    min = np.ceil(np.amin(tri, axis = 1)).astype(int)
    max = np.floor(np.amax(tri, axis = 1)).astype(int)

    sum = np.array([0, 0, 0])
    num_of_pixels = 0

    for x in range(min[0], max[0] + 1):
        for y in range(min[1], max[1] + 1):
            if in_trinagle([x, y], tri):
                sum += img[y, x]
                num_of_pixels += 1

    num_of_pixels = 1 if num_of_pixels == 0 else num_of_pixels
    return tuple(sum / num_of_pixels / 255)


def random_delaunay(img, n):
    h,w = img.shape[:2]

    x = np.random.rand(n) #* (w - 1)
    y = np.random.rand(n) #* (h - 1)

    dln = tri.Triangulation(x, y)

    return dln


def delaunay_color(img, dln):
    colors = np.zeros([dln.x.shape[0], 3])

    for ind in range(dln.x.size):
        triang = np.array([dln.x[dln.triangles[ind]], dln.y[dln.triangles[ind]]])
        colors[ind] = color_sum(img, triang)
    return colors


if __name__ == "__main__":
    print("Trimath main")
    import cv2
    img = cv2.imread('trees.jpeg')

    dln = random_delaunay(img, 100)

    # colors = delaunay_color(img, dln)

    from plotter import plot_triangles
    colors = tuple([[0.5, 0.3, 0.7], [0.1, 0.4, 0.2]])

    N = 1000
    from matplotlib.tri import Triangulation

    points = np.random.rand(N,2) * 2
    dln = Triangulation(points[:, 0], points[:, 1])
    plot_triangles(dln, colors, img.shape[1:])

    print("Finished")








