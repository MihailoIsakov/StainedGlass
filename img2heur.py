__author__ = 'zieghailo'

import numpy as np


def default_focus_image(img):
    return np.ones(img.shape[:2]).astype(np.uint16)


def linear(img):
    h = img / 25.5
    h = np.ceil(h)
    return h.astype(np.uint16)


def grayscale(img):
    import cv2
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)