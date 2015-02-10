#! /usr/bin/env python

__author__ = 'zieghailo'

from mesh import Mesh
import trimath
from support import plotter
from support.meshcollection import FlatMeshCollection

import cv2
import numpy as np
from time import time

IMAGE_URI       = 'images/lion.jpg'
STARTING_POINTS = 500
TEMPERATURE     = 30
TEMP_MULTIPLIER = 0.999
MAX_ERR         = 10**5
MIN_ERR         = 10**5
PURGE_COUNTER   = 10*100
PARALLEL        = True
PRINT           = True
PRINT_COUNTER   = 30
PRINT_TIME      = False

# region needed so that @profile doesn't cause an error
import __builtin__

try:
    __builtin__.profile
except AttributeError:
    # No line profiler, provide a pass-through version
    def profile(func): return func
    __builtin__.profile = profile
# endregion

@profile
def main():
    global mesh

    img = cv2.imread(IMAGE_URI)
    cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
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

        print("Temperature: "+str(pixtemp))
        purge = not bool((cnt + 1) % PURGE_COUNTER)

        mesh.evolve(pixtemp, percentage=0.02, purge=purge, maxerr=MAX_ERR, minerr=MIN_ERR, parallel=PARALLEL)
        if purge:
            print("Purging points: "+str(len(mesh.points)) + " points")

        # print()
        from SApoint import SApoint
        # print(SApoint.switched, SApoint.notswitched)

        pixtemp *= TEMP_MULTIPLIER

        # region print time
        if PRINT_TIME:
            now = time()
            print("Time elapsed: ", now - past)
            past = now
        #endregion

        plotter.plot_global_errors(mesh.error)

        if (cnt % PRINT_COUNTER == (PRINT_COUNTER - 1)):

            col = FlatMeshCollection(mesh)
            # plotter.plot_points(mesh)
            # plotter.plot_arrow(mesh)
            plotter.plot_mesh_collection(col)
            # plotter.plot_error_hist(mesh.point_errors, mesh.triangle_errors)

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()
