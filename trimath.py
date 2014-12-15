__author__ = 'zieghailo'

import numpy as np
from collections import namedtuple
import functools
import multiprocessing

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

Rect = namedtuple('Rect', ['north', 'south', 'east', 'west'])
def triangle_sum(img, tr, get_error=False):
    """
    Returns the average RGB value for the pixels in the triangle tr,
    for the image img.
    :param img: The image for which we're returning the average triangle color
    :param tr: The 3x2 numpy array defining the triangle vertices
    :param get_error: Boolean value choosing if we make another loop, calculating
    the absolute color error in the triangle
    :return: The average color and the absolute error
    """
    _north = np.ceil(np.amax(tr[1])).astype(int)
    _south = np.floor(np.amin(tr[1])).astype(int)
    _east  = np.ceil(np.amax(tr[0])).astype(int)
    _west  = np.floor(np.amin(tr[0])).astype(int)
    rect = Rect(_north, _south, _east, _west)

    num_of_pixels = 0
    sum = np.array([0, 0, 0])
    bounds = np.zeros([rect.north - rect.south + 1, 2])

    for y in range(rect.south, rect.north + 1):
        sol = _y_intersects(y, tr)
        sol = sol[rect.west <= sol]
        sol = sol[sol <= rect.east]

        if sol.size == 0:
            continue

        left  = np.round(np.amin(sol)).astype(int)
        right = np.round(np.amax(sol)).astype(int)
        bounds[y - rect.south] = [left, right]

        # TODO figure out why we access by (y,x) instead of (x,y)
        try:
            sum += np.sum(img[y, left:right + 1], axis = 0)
            num_of_pixels += right - left + 1
        except Exception:
            pass

    num_of_pixels = 1 if num_of_pixels == 0 else num_of_pixels
    sum[0], sum[2] = sum[2], sum[0] # cv2 issues
    color = sum / num_of_pixels

    error = np.array(0)
    if get_error:
        for y in range(rect.south, rect.north + 1): # get the error of the triangle
            # error += np.sum(np.linalg.norm())
            left = bounds[y - rect.south, 0]
            right = bounds[y - rect.south, 1]
            error += np.sum(np.linalg.norm(np.linalg.norm(img[y, left:right + 1] - color)))
        return tuple(color / 255.0), error

    return tuple(color / 255.0)

def parallel_sum(img ,tr, get_error=False):
    _north = np.ceil(np.amax(tr[1])).astype(int)
    _south = np.floor(np.amin(tr[1])).astype(int)
    _east  = np.ceil(np.amax(tr[0])).astype(int)
    _west  = np.floor(np.amin(tr[0])).astype(int)
    rect = Rect(_north, _south, _east, _west)

    num_of_pixels = 0
    sum = np.array([0, 0, 0])
    bounds = np.zeros([rect.north - rect.south + 1, 2])

    pool = multiprocessing.Pool(processes=8)
    f = functools.partial(_sum_row, img, tr, rect=rect)
    res = pool.map(f, range(rect.south, rect.north + 1))
    pool.close()
    pool.join()

    sum += np.sum(np.array([c[0] for c in res]))
    num_of_pixels += np.sum(np.array([n[1] for n in res]))
    bounds = np.array([b[2] for b in res])

    f = functools.partial(_sum_row_error, img, sum, rect=rect, bounds=bounds)
    pool = multiprocessing.Pool(processes=8)
    res = pool.map(f, range(rect.south, rect.north + 1))
    pool.close()
    pool.join()

    num_of_pixels = 1 if num_of_pixels == 0 else num_of_pixels
    sum[0], sum[2] = sum[2], sum[0] # cv2 issues
    color = sum / num_of_pixels
    error = np.sum(res)

    return color, error


def _sum_row_error(img, color, y, rect, bounds):
    error = 0
    left = bounds[y - rect.south, 0]
    right = bounds[y - rect.south, 1]
    error += np.sum(np.linalg.norm(np.linalg.norm(img[y, left:right + 1] - color)))
    return error


def _sum_row(img, tr, y, rect):
    num_of_pixels = 0
    sum = np.array([0, 0, 0])

    sol = _y_intersects(y, tr)
    sol = sol[rect.west <= sol]
    sol = sol[sol <= rect.east]

    if sol.size == 0:
        return []

    left  = np.round(np.amin(sol)).astype(int)
    right = np.round(np.amax(sol)).astype(int)
    bounds = [left, right]

    # TODO figure out why we access by (y,x) instead of (x,y)
    try:
        sum += np.sum(img[y, left:right + 1], axis = 0)
        num_of_pixels += right - left + 1
    except Exception:
        pass

    return sum, num_of_pixels, bounds


def rand_point_in_triangle(tr):
    A = tr[:, 0]
    B = tr[:, 1]
    C = tr[:, 2]
    AB = B - A
    AC = C - A

    k = 1; s = 1
    while k + s > 1:
        k = np.random.rand()
        s = np.random.rand()

    point = A + AB * k + AC * s
    return point
