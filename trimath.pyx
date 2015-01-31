__author__ = 'zieghailo'

# cython: profile=True

import numpy as np
import cython
cimport cython
cimport numpy as np

from cv2 import fillConvexPoly
from collections import namedtuple
from scipy.spatial.qhull import Delaunay

ctypedef np.float64_t FLOAT_t

Rect = namedtuple('Rect', ['north', 'south', 'east', 'west'])

# The image being processed, in module scope so that map doesn't require multiple arguments
# cdef np.uint8_t[:, :, :] IMAGE

def set_image(np.ndarray[np.uint8_t, ndim=3] img):
    global IMAGE
    IMAGE = img

cdef np.ndarray[np.uint8_t, ndim=3] get_image():
    global IMAGE
    return IMAGE


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


def _get_rect(tr):
    _north = np.ceil(np.amax(tr[1])).astype(int)
    _south = np.floor(np.amin(tr[1])).astype(int)
    _east  = np.ceil(np.amax(tr[0])).astype(int)
    _west  = np.floor(np.amin(tr[0])).astype(int)
    return Rect(_north, _south, _east, _west)


cdef np.ndarray[np.int_t, ndim=1] _get_rect_nsew(np.ndarray[FLOAT_t, ndim=2] tr):
    cdef int north = np.ceil(np.amax(tr[1])).astype(int)
    cdef int south = np.floor(np.amin(tr[1])).astype(int)
    cdef int east  = np.ceil(np.amax(tr[0])).astype(int)
    cdef int west  = np.floor(np.amin(tr[0])).astype(int)
    return np.array([north, south, east, west])

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


@cython.boundscheck(False)
@cython.cdivision(True)
def cv2_triangle_sum(np.ndarray[FLOAT_t, ndim=2] tr):
    """
    Creates a binary mask of pixels inside the triangle,
    and multiplies it with the image.
    It then calculates the sum of the whole matrix.
    :param img: The minimal image containing the triangle, defined by _get_rect
    :param tr:  The global triangle coordinates, 2x3 numpy array
    :return: The color, error_sum, and number of pixels
    """

    cdef np.ndarray[np.uint8_t, ndim=3] IMAGE = get_image()

    cdef np.ndarray[np.uint8_t, ndim=3] cutout = _image_cutout(IMAGE, tr)
    cdef np.ndarray[FLOAT_t, ndim=2] reltr = _relative_triangle(tr)
    cdef np.ndarray[np.long_t, ndim=2] normtr = reltr.round().astype(int).transpose()

    cdef np.ndarray[np.uint8_t, ndim=2] mask = _make_mask(cutout, normtr)
    cdef np.uint64_t pixnum = np.sum(mask)

    if pixnum == 0:
        return (0,0,0), 0

    # cdef int maxx, maxy
    # maxx = cutout.shape[0]
    # maxy = cutout.shape[1]

    cdef FLOAT_t red = 0
    cdef FLOAT_t blue = 0
    cdef FLOAT_t green = 0

    red = np.sum(cutout[:, :, 0] * mask)
    green = np.sum(cutout[:, :, 1] * mask)
    blue = np.sum(cutout[:, :, 2] * mask)

    # for x in range(maxx):
    #     for y in range(maxy):
    #         red   += cutout[x, y, 0] * mask[x, y]
    #         green += cutout[x, y, 1] * mask[x, y]
    #         blue  += cutout[x, y, 2] * mask[x, y]

    red = red / pixnum
    blue = blue / pixnum
    green = green / pixnum

    cdef FLOAT_t red_err   = 0
    cdef FLOAT_t green_err = 0
    cdef FLOAT_t blue_err  = 0

    red_err = np.sum(np.abs(cutout[:, :, 0] - red) * mask)
    green_err = np.sum(np.abs(cutout[:, :, 1] - green) * mask)
    blue_err = np.sum(np.abs(cutout[:, :, 2] - blue) * mask)
    # x = 0
    # y = 0

    # for x in range(maxx):
    #     for y in range(maxy):
    #         red_err   += np.abs(cutout[x, y, 0] * mask[x, y] - red)
    #         green_err += np.abs(cutout[x, y, 1] * mask[x, y] - green)
    #         blue_err  += np.abs(cutout[x, y, 2] * mask[x, y] - blue)

    cdef FLOAT_t error = red_err + green_err + blue_err
    color = (red / 255.0, green / 255.0, blue / 255.0)
    return color, error


cdef _make_mask(np.ndarray[np.uint8_t, ndim=3] cutout, np.ndarray[np.long_t, ndim=2] rel_tri):
    cdef np.ndarray[np.uint8_t, ndim=2] mask = np.zeros([cutout.shape[0], cutout.shape[1]], dtype=np.uint8)
    fillConvexPoly(mask, rel_tri, 1)
    return mask


cdef np.ndarray[np.uint8_t, ndim=3] _image_cutout(np.ndarray[np.uint8_t, ndim=3] img, np.ndarray[FLOAT_t, ndim=2] tr):
    rect = _get_rect(tr)
    cdef np.ndarray[np.uint8_t, ndim=3] cutout = img[rect.south:rect.north, rect.west:rect.east]
    return cutout


cdef _relative_triangle(np.ndarray[FLOAT_t, ndim=2] tr):
    cdef np.ndarray[np.int_t, ndim=1] nsew = _get_rect_nsew(tr)
    cdef np.ndarray[FLOAT_t, ndim=2] newtr = np.copy(tr)
    newtr[0] -= nsew[3]
    newtr[1] -= nsew[1]
    return newtr
