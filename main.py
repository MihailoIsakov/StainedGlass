#! /usr/bin/env python

__author__ = 'zieghailo'

from mesh import Mesh
import trimath
from support import plotter
from support.meshcollection import FlatMeshCollection

import cv2
import numpy as np
from time import time

# region needed so that @profile doesn't cause an error
import __builtin__

try:
    __builtin__.profile
except AttributeError:
    # No line profiler, provide a pass-through version
    def profile(func): return func
    __builtin__.profile = profile
# endregion

from settings.christmas_settings import *

@profile
def main():
    global mesh

    img = cv2.imread(IMAGE_URI)
    cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
    img = np.flipud(img)

    trimath.set_image(img)

    mesh = Mesh(img, STARTING_POINTS, parallel=PARALLEL)
    mesh.triangulate(True)

    col = FlatMeshCollection(mesh._triangulation)
    plotter.start()
    plotter.plot_mesh_collection(col)
    past = time()

    pixtemp = TEMPERATURE  # pixels radius

    for cnt in range(10**6):

        purge = not bool((cnt + 1) % PURGE_COUNTER)
        mesh.evolve(pixtemp,
                    percentage=POINT_SHIFT_PERCENTAGE,
                    purge=purge,
                    maxerr=MAX_ERR, minerr=MIN_ERR,
                    parallel=PARALLEL)
        pixtemp *= TEMP_MULTIPLIER

        # region print time
        if PRINT_CONSOLE:
            print("Temperature: "+str(pixtemp))
            now = time()
            print("Time elapsed: ", now - past)
            past = now
        #endregion

        plotter.plot_global_errors(mesh._error)
        if (cnt % PRINT_COUNTER == (PRINT_COUNTER - 1)):
            col = FlatMeshCollection(mesh._triangulation)
            plotter.plot_points(mesh)
            plotter.plot_arrow(mesh)
            plotter.plot_mesh_collection(col)
            # plotter.plot_error_hist(mesh.point_errors, mesh.triangle_errors)

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()
