__author__ = 'zieghailo'

import numpy as np

def get_point_error(dln, error):
    point_error = np.zeros(dln.x.shape)
    for tri_index in dln.triangles.shape: # go through triangles
        for vert in dln.triangles[tri_index]: # and their points
            point_error[vert] += error[tri_index] # and to each point add the triangles error

    return point_error


def cull_100_weak(dln, point_error, epsilon):
    pe = np.copy(point_error)
    pe.sort()
    return (dln.x[:-100], dln.y[:-100])


def check_if_weak(dln, point_index, point_error, epsilon):
    if point_error < epsilon:
        return True
    return False

