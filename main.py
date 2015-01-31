#! /usr/bin/env python

__author__ = 'zieghailo'

from mesh import Mesh
import trimath
from support import plotter
from support.meshcollection import FlatMeshCollection

import cv2
import numpy as np
from time import time

IMAGE_URI       = 'images/renoir.jpg'
STARTING_POINTS = 100
TEMPERATURE     = 20
TEMP_MULTIPLIER = 0.997
MAX_ERR         = 10 ** 6
MIN_ERR         = 10 ** 5
PURGE_COUNTER   = 10**60
PARALLEL        = True
PRINT_COUNTER   = 5

@profile
def main():
    global mesh

    img = cv2.imread(IMAGE_URI)
    img = np.flipud(img)
    trimath.set_image(img)

    mesh = Mesh(img, STARTING_POINTS, parallel=PARALLEL)
    mesh.triangulate(True)

    col = FlatMeshCollection(mesh)
    plotter.start()
    plotter.plot_mesh_collection(col)
    past = time()

    pixtemp = TEMPERATURE  # pixels radius

    for cnt in range(10**6):

        print("Temperature: "+ str(pixtemp))
        purge = not bool((cnt + 1) % PURGE_COUNTER)

        mesh.evolve(pixtemp, purge, maxerr=MAX_ERR, minerr=MIN_ERR, parallel=PARALLEL)
        if purge:
            print("Purging points: "+ str(len(mesh.points)) + " points")

        print()
        from SApoint import SApoint
        print(SApoint.switched, SApoint.notswitched)

        pixtemp *= TEMP_MULTIPLIER

        now = time()
        print("Time elapsed: ", now - past)
        past = now

        plotter.plot_global_errors(mesh.error)

        if cnt % PRINT_COUNTER == 0:
            col = FlatMeshCollection(mesh)
            # plotter.plot_points(mesh)
            # plotter.plot_arrow(mesh)
            plotter.plot_mesh_collection(col)
            mesh.update_errors()
            plotter.plot_error_hist(mesh.point_errors, mesh.triangle_errors)

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()
