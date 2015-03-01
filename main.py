#! /usr/bin/env python

__author__ = 'zieghailo'

from mesh import Mesh
import trimath
from support import plotter
from support.meshcollection import FlatMeshCollection
from support.profiler_fix import *


import cv2
import numpy as np
from time import time

from settings.renoir_settings import *


@profile
def main():
    global mesh

    img = cv2.imread(IMAGE_URI)
    cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
#    img = np.flipud(img)

    trimath.set_image(img)

    mesh = Mesh(img, STARTING_POINTS, parallel=PARALLEL)
    mesh.triangulate(True)

    col = FlatMeshCollection(mesh._triangulation, alpha=TRIANGLE_ALPHA)
    plotter.start()
    plotter.plot_original(img, 1 - TRIANGLE_ALPHA)
    plotter.plot_mesh_collection(col)
    past = time()

    pixtemp = TEMPERATURE  # pixels radius

    for cnt in range(10 ** 6):

        # The chance to purge points.
        # In the beginning when pixtemp is almost TEMPERATURE,
        # the chance to purge is high. As the temperature gets lower,
        # the chance to purge approaches zero.
        purge = np.random.rand() * PURGE_MULTIPLIER < pixtemp / TEMPERATURE

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
            print TRIANGLE_ALPHA
            col = FlatMeshCollection(mesh._triangulation, alpha=TRIANGLE_ALPHA)
            #plotter.plot_points(mesh)
            #plotter.plot_arrow(mesh)
            plotter.plot_original(img, 1 - TRIANGLE_ALPHA)
            plotter.plot_mesh_collection(col)
            # plotter.plot_error_hist(mesh.point_errors, mesh.triangle_errors)

    plotter.keep_plot_open()


def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(prog='Stained Glass',
                                     description='Create a low poly version '
                                                 'of a given image.')
    parser.add_argument('filename')
    parser.add_argument('-t', '--temperature', type=float, dest='TEMPERATURE')
    parser.add_argument('-p', '--points',      type=int,   dest='STARTING_POINTS')
    parser.add_argument('-m', '--multiplier',  type=float, dest='TEMP_MULTIPLIER')
    parser.add_argument('-c', '--console',     type=bool,  dest='PRINT_CONSOLE')
    parser.add_argument('-d', '--draw',        type=int,   dest='PRINT_COUNTER')

    args = parser.parse_args()
    print args
    return args


if __name__ == "__main__":

    globals().update(vars(parse_arguments()))

    main()
