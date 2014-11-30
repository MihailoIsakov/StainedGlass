__author__ = 'zieghailo'

import sys
import numpy as np
import matplotlib.tri as tri
from plotter import plot_triangles


def in_trinagle(point, triangle):
    """
    Check if point is inside the triangle
    :param point: two element numpy.array, p = [x,y]
    :param triangle: 2x3 numpy.array of the triangle vertices
    :return: True if the point is in the triangle
    """
    mat = np.copy(triangle[:, 1:])
    mat[:,0] -= triangle[:,0]
    mat[:,1] -= triangle[:,0]
    p = point - triangle[:,0]

    x = np.linalg.solve(mat, p)

    return 0 <= x[0] <= 1 and 0 <= x[1] <= 1 and x[0] + x[1] <= 1


def color_sum(img, tri):
    min = np.floor(np.amin(tri, axis = 1)).astype(int)
    max = np.ceil(np.amax(tri, axis = 1)).astype(int)

    sum = np.array([0, 0, 0])
    num_of_pixels = 0

    for x in range(min[0], max[0] + 1):
        for y in range(min[1], max[1] + 1):
            if in_trinagle([x, y], tri):
                sum += img[y, x]
                num_of_pixels += 1

    num_of_pixels = 1 if num_of_pixels == 0 else num_of_pixels
    sum[0], sum[2] = sum[2], sum[0] # cv2 issues
    return tuple(sum / num_of_pixels / 255.0)


def random_delaunay(img, n):
    h,w = img.shape[:2]

    x = np.random.rand(n) * (w - 1)
    y = np.random.rand(n) * (h - 1)

    x[0:4] = [0, w-1, 0, w-1]
    y[0:4] = [0, 0, h-1, h-1]

    dln = tri.Triangulation(x, y)

    return dln


def delaunay_color(img, dln):
    colors = np.zeros([dln.triangles.shape[0], 3])
    l = dln.triangles.shape[0]

    for ind in range(dln.triangles.shape[0]):
        sys.stdout.write('\r[' + '-' * (50 * ind / l) + ' ' * (50 - 50 * ind / l) + ']')
        triang = np.array([dln.x[dln.triangles[ind]], dln.y[dln.triangles[ind]]])
        colors[ind] = color_sum(img, triang)
    return colors


def main():
    print("Trimath main")
    import cv2
    img = cv2.imread('images/tara.jpg')
    img = np.flipud(img)

    print "Running Delaunay triangulation"
    dln = random_delaunay(img, 5000)

    print "Caluclating triangle colors"
    colors = delaunay_color(img, dln)

    print "Plotting triangles"
    plot_triangles(dln, colors)

    print("Finished")


if __name__ == "__main__":
    main()








