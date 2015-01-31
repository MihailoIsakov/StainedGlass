__author__ = 'zieghailo'

import numpy as np
import numpy.ma as ma
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


def set_image(img):
    global _image
    _image = img


def triangle_sum_sw(tr, img):
    return triangle_sum(img, tr)


def _get_rect(tr):
    _north = np.ceil(np.amax(tr[1])).astype(int)
    _south = np.floor(np.amin(tr[1])).astype(int)
    _east  = np.ceil(np.amax(tr[0])).astype(int)
    _west  = np.floor(np.amin(tr[0])).astype(int)
    return Rect(_north, _south, _east, _west)


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


@profile
def triangle_sum(tr):
    """
    Creates a binary mask of pixels inside the triangle,
    and multiplies it with the image.
    It then calculates the sum of the whole matrix.
    :param img: The minimal image containing the triangle, defined by _get_rect
    :param tr:  The global triangle coordinates, 2x3 numpy array
    :return: The color, error_sum, and number of pixels
    """
    global _image
    cutout = _image_cutout(_image, tr)
    mask = _make_mask(cutout, tr)
    pixnum = np.sum(np.invert(mask == 1))
    msk_shp = [mask.shape[0], mask.shape[1], 1]
    mask = np.reshape(mask, msk_shp).repeat(3, 2)

    if pixnum <= 0:
        return (0, 0, 0,), 0, 0

    maskimg = ma.array(cutout[:, :], mask=mask)
    color = np.mean(np.mean(maskimg, 0), 0)
    error_matrix = maskimg - color

    #relative error
    error = np.sum(np.abs(error_matrix))
    # error = _relative_error(error, pixnum)

    assert type(error) is not np.ma.core.MaskedConstant

    color[2], color[0] = color[0], color[2]  #cv2 issues, BGR instead of RGB
    color = tuple(color / 255.0)

    return color, error


def _relative_error(abs_error, pix):
    return abs_error / pix.astype(float) / 255.0


def _make_mask(cutout, tr):
    rel_tri = _relative_triangle(tr).round().astype(int).transpose()
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