__author__ = 'zieghailo'

import numpy as np
from collections import namedtuple
from warnings import simplefilter
from scipy.spatial.qhull import Delaunay


Rect = namedtuple('Rect', ['north', 'south', 'east', 'west'])


def DelaunayXY(x, y):
    global p
    x = x.reshape(1, x.size)
    y = y.reshape(1, y.size)

    p = np.concatenate((x, y))
    p = p.transpose()

    try:
        d = Delaunay(p)
    except Exception:
        pass
    return d


def in_triangle(point, triangle):
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


def _y_intersects(y, tr):
    """
    Returns the points where the triangle lines intersect the horizontal y line
    :param y: height of the horizontal line
    :param tr: triangle 2x3 numpy array
    :return: the three points where the line intersects the lines. Some may be NaN in case of a horizontal line.
    """
    # TODO: probably can be replaced by a faster numpy routine
    with np.errstate(invalid='ignore', divide='ignore'):
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


def triangle_sum(img, tr):
    """
    Returns the average RGB value for the pixels in the triangle tr,
    for the image img.
    :param img: The image for which we're returning the average triangle color
    :param tr: The 3x2 numpy array defining the triangle vertices
    :param get_error: Boolean value choosing if we make another loop, calculating
    the absolute color error in the triangle
    :return: The average color and the absolute error
    """
    rect = _get_rect(tr)
    num_of_pixels = 0
    color = np.array([0, 0, 0])
    borders = _get_borders(tr)

    for y in range(rect.south, rect.north + 1):
        dy = y - rect.south
        s, n = _sum_row(img, y, borders[dy])
        color += s
        num_of_pixels += n

    num_of_pixels = max(num_of_pixels, 1)
    color[0], color[2] = color[2], color[0] # cv2 issues
    color = color / num_of_pixels

    error = np.array(0)
    for y in range(rect.south, rect.north + 1): # get the error of the triangle
        dy = y - rect.south
        error += _sum_row_error(img, color, y, borders[dy])
    return tuple(color / 255.0), error


def _get_rect(tr):
    _north = np.ceil(np.amax(tr[1])).astype(int)
    _south = np.floor(np.amin(tr[1])).astype(int)
    _east  = np.ceil(np.amax(tr[0])).astype(int)
    _west  = np.floor(np.amin(tr[0])).astype(int)
    return Rect(_north, _south, _east, _west)


def _get_borders(tr):
    rect = _get_rect(tr)

    borders = np.zeros([rect.north - rect.south + 1, 2])
    for y in range(rect.south, rect.north + 1):
        sol = _y_intersects(y, tr)
        simplefilter('ignore', RuntimeWarning)
        sol = sol[rect.west <= sol]
        sol = sol[sol <= rect.east]

        if sol.size == 0:
            continue

        left  = np.round(np.amin(sol)).astype(int)
        right = np.round(np.amax(sol)).astype(int)
        borders[y - rect.south] = [left, right]

    return borders


def _sum_row_error(img, color, y, bounds):
    left = bounds[0]
    right = bounds[1]
    try:
        error = np.sum(np.linalg.norm(np.linalg.norm(img[y, left:right + 1] - color)))
    except Exception:
        error = 0

    return error


def _sum_row(img, y, bounds):
    """
    Sums the pixels at y height betwwen the borders
    :param img: pixel matrix
    :param y: row height
    :param bounds: 2x1 array of borders
    :return: sum of pixels
    """
    sum = [0, 0, 0]
    num_of_pixels = 0
    left = bounds[0]
    right = bounds[1]
    # TODO figure out why we access by (y,x) instead of (x,y)
    try:
        sum = np.sum(img[y, left:right + 1], axis=0)
        num_of_pixels = right - left + 1
    except Exception:
        pass

    return sum, num_of_pixels


def rand_point_in_triangle(tr):
    A = tr[:, 0]
    B = tr[:, 1]
    C = tr[:, 2]
    AB = B - A
    AC = C - A

    while True:
        k = np.random.rand()
        s = np.random.rand()
        if k + s <= 1:
            break

    point = A + AB * k + AC * s
    return point
