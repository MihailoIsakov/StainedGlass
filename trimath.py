__author__ = 'zieghailo'

import sys
import numpy as np
import matplotlib.tri as tri
from plotter import plot_triangles


def _y_intersects(y, tr):
    """
    Returns the points where the triangle lines intersect the horizontal y line
    :param y: height of the horizontal line
    :param tr: triangle 2x3 numpy array
    :return: the three points where the line intersects the lines. Some may be NaN in case of a horizontal line.
    """
    diffAB = tr[:, 1] - tr[:, 0]
    diffAC = tr[:, 2] - tr[:, 0]
    diffBC = tr[:, 2] - tr[:, 1]

    kAB = diffAB[1] / diffAB[0]
    kAC = diffAC[1] / diffAC[0]
    kBC = diffBC[1] / diffBC[0]

    dxab = (y - tr[1, 0]) / kAB
    xab = tr[0, 0] + dxab
    dxac = (y - tr[1, 0]) / kAC
    xac = tr[0, 0] + dxac
    dxbc = (y - tr[1, 1]) / kBC
    xbc = tr[0, 1] + dxbc

    return np.array([xab, xac, xbc])


def triangle_sum(img, tr, get_error = False):
    north = np.floor(np.amax(tr[1,:])).astype(int)
    south = np.ceil (np.amin(tr[1,:])).astype(int)
    east  = np.floor(np.amax(tr[0,:])).astype(int)
    west  = np.ceil (np.amin(tr[0,:])).astype(int)

    num_of_pixels = 0
    sum = np.array([0, 0, 0])
    error = np.array([0, 0, 0])
    bounds = np.zeros([north - south + 1, 2])

    for y in range(south, north + 1):
        sol = _y_intersects(y, tr)
        sol = sol[west <= sol]
        sol = sol[sol <= east]

        if sol.size == 0:
            continue

        left  = np.round(np.amin(sol)).astype(int)
        right = np.round(np.amax(sol)).astype(int)
        bounds[y - south] = [left, right]

        sum += np.sum(img[left:right + 1, y], axis = 0)
        num_of_pixels += right - left + 1

    num_of_pixels = 1 if num_of_pixels == 0 else num_of_pixels
    sum[0], sum[2] = sum[2], sum[0] # cv2 issues
    color = sum / num_of_pixels

    if get_error:
        for y in range(south, north + 1): # get the error of the triangle
            error += np.sum(np.linalg.norm(img[bounds[y - south, 0] : bounds[y - south, 1]] - color))

    return tuple(color / 255.0)


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
        colors[ind] = triangle_sum(img, triang)

    print ' '
    return colors


def main():
    np.seterr(all = 'ignore')

    print("Trimath main")
    import cv2
    img = cv2.imread('images/tara.jpg')
    # img = np.flipud(img)

    print "Running Delaunay triangulation"
    dln = random_delaunay(img, 500)

    print "Caluclating triangle colors"
    colors = delaunay_color(img, dln)

    print "Plotting triangles"
    plot_triangles(dln, colors)

    print("Finished")


if __name__ == "__main__":
    main()








