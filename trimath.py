__author__ = 'zieghailo'

import numpy as np
from cv2 import fillConvexPoly
from collections import namedtuple
from scipy.spatial.qhull import Delaunay


Rect = namedtuple('Rect', ['north', 'south', 'east', 'west'])


# region needed so that @profile doesn't cause an error
import __builtin__

try:
    __builtin__.profile
except AttributeError:
    # No line profiler, provide a pass-through version
    def profile(func): return func
    __builtin__.profile = profile
# endregion


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


@profile
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

@profile
def _get_borders(tr):
    rect = _get_rect(tr)

    borders = np.zeros([rect.north - rect.south + 1, 2])
    for y in range(rect.south, rect.north + 1):
        sol = _y_intersects(y, tr)
        # simplefilter('ignore', RuntimeWarning)
        sol = sol[rect.west <= sol]
        sol = sol[sol <= rect.east]

        if sol.size == 0:
            continue

        left  = np.round(np.amin(sol)).astype(int)
        right = np.round(np.amax(sol)).astype(int)
        borders[y - rect.south] = [left, right]

    return borders

@profile
def _sum_row_error(img, color, y, bounds):
    left = bounds[0]
    right = bounds[1]
    try:
        error = np.sum(np.linalg.norm(np.linalg.norm(img[y, left:right + 1] - color)))
    except Exception:
        error = 0

    return error

@profile
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


def cv2_triangle_sum(img, tr):
    """
    Creates a binary mask of pixels inside the triangle,
    and multiplies it with the image.
    It then calculates the sum of the whole matrix.
    :param img: The minimal image containing the triangle, defined by _get_rect
    :param tr:  The global triangle coordinates, 2x3 numpy array
    :return: The color, error_sum, and number of pixels
    """

    cutout = _image_cutout(img, tr)
    reltr = _relative_triangle(tr)
    trnorm = reltr.round().astype(int).transpose()

    mask = _make_mask(cutout, trnorm)
    pixnum = np.sum(mask)

    red   = np.sum(cutout[:, :, 0] * mask) / pixnum
    green = np.sum(cutout[:, :, 1] * mask) / pixnum
    blue  = np.sum(cutout[:, :, 2] * mask) / pixnum

    # Get the difference between the color and the error
    cutout[:, :, 0] -= red
    cutout[:, :, 1] -= green
    cutout[:, :, 2] -= blue
    cutout = np.abs(cutout)

    red_error   = np.sum(cutout[:, :, 0] * mask)
    green_error = np.sum(cutout[:, :, 1] * mask)
    blue_error  = np.sum(cutout[:, :, 2] * mask)
    error = red_error + green_error + blue_error

    color = (red / 255.0, green / 255.0, blue / 255.0)
    return color, error, pixnum


def _make_mask(cutout, rel_tri):
    mask = np.zeros([cutout.shape[0], cutout.shape[1]])
    fillConvexPoly(mask, rel_tri, 1)
    return mask


def _image_cutout(img, tr):
    rect = _get_rect(tr)
    cutout = img[rect.south:rect.north, rect.west:rect.east]
    return cutout


def _relative_triangle(tr):
    rect = _get_rect(tr)
    newtr = np.copy(tr)

    newtr[0] -= rect.west
    newtr[1] -= rect.south

    return newtr


if __name__ == "__main__":
    import cv2
    img1 = cv2.imread('images/lion.jpg')
    img2 = np.copy(img1)

    import numpy as np
    tr = np.array([[100, 200, 300], [300, 100, 200]])

    print "cv2 triangle sum: "
    res1 = cv2_triangle_sum(img1, tr)
    print res1

    print "old triangle sum"
    res2 = triangle_sum(img2, tr)
    print res2
