#! /usr/bin/env python

__author__ = 'zieghailo'

from mesh import Mesh
import trimath
from support import plotter
from support.meshcollection import FlatMeshCollection

import cv2
import numpy as np
from time import time

from support.profiler_fix import *
from settings.renoir_settings import *

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

    for cnt in range(10 ** 6):

        # The chance to purge points.
        # In the beginning when pixtemp is almost TEMPERATURE,
        # the chance to purge is high. As the temperature gets lower,
        # the chance to purge approaches zero.
        purge = np.random.rand() < pixtemp / TEMPERATURE

        mesh.evolve(pixtemp,
                    purge=purge,
                    parallel=PARALLEL)
        pixtemp *= TEMP_MULTIPLIER

        # region print time
        if PRINT_CONSOLE:
            print("Temperature: "+str(pixtemp))
            now = time()
            print("Time elapsed: ", now - past)
            past = now
        #endregion

        if (cnt % PRINT_ERROR_COUNTER == 0):
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
