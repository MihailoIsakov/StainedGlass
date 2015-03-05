__author__ = 'zieghailo'

import cv2, numpy as np


def load_heur_image(image_uri):
    img = cv2.imread(image_uri)
    gsimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gsimg


def pixel2heur(val):
    val = val.astype(np.uint16)
    val *= 10
    return val

