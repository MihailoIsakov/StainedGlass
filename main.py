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


@profile
def main(C):
    global mesh

    img = cv2.imread(C.IMAGE_URI)
    cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
#    img = np.flipud(img)

    trimath.set_image(img)

    mesh = Mesh(img, C.STARTING_POINTS, parallel=C.PARALLEL)
    mesh.triangulate(True)

    col = FlatMeshCollection(mesh._triangulation, alpha=C.TRIANGLE_ALPHA)
    plotter.start()
    plotter.plot_original(img, 1 - C.TRIANGLE_ALPHA)
    plotter.plot_mesh_collection(col)

    past = time()
    pixtemp = C.TEMPERATURE  # pixels radius

    for cnt in range(10 ** 6):

        # The chance to purge points.
        # In the beginning when pixtemp is almost TEMPERATURE,
        # the chance to purge is high. As the temperature gets lower,
        # the chance to purge approaches zero.
        purge = np.random.rand() * C.PURGE_MULTIPLIER < pixtemp / C.TEMPERATURE

        mesh.evolve(pixtemp,
                    purge=purge,
                    parallel=C.PARALLEL)
        pixtemp *= C.TEMP_MULTIPLIER

        # region print time
        if C.PRINT_CONSOLE:
            print("Temperature: "+str(pixtemp))
            now = time()
            print("Time elapsed: ", now - past)
            past = now
        #endregion

        if (cnt % C.PRINT_ERROR_COUNTER == 0):
            plotter.plot_global_errors(mesh._error)

        if (cnt % C.PRINT_COUNTER == (C.PRINT_COUNTER - 1)):
            print C.TRIANGLE_ALPHA
            col = FlatMeshCollection(mesh._triangulation, alpha=C.TRIANGLE_ALPHA)
            #plotter.plot_points(mesh)
            #plotter.plot_arrow(mesh)
            plotter.plot_original(img, 1 - C.TRIANGLE_ALPHA)
            plotter.plot_mesh_collection(col)
            # plotter.plot_error_hist(mesh.point_errors, mesh.triangle_errors)

    plotter.keep_plot_open()


def parse_arguments(default_settings):
    import argparse
    parser = argparse.ArgumentParser(prog='Stained Glass',
                                     description='Create a low poly version '
                                                 'of a given image.')
    parser.add_argument('IMAGE_URI')
    parser.add_argument('-t', '--temperature', type=float, dest='TEMPERATURE')
    parser.add_argument('-p', '--points',      type=int,   dest='STARTING_POINTS')
    parser.add_argument('-m', '--multiplier',  type=float, dest='TEMP_MULTIPLIER')
    parser.add_argument('-c', '--console',     type=bool,  dest='PRINT_CONSOLE')
    parser.add_argument('-d', '--draw',        type=int,   dest='PRINT_COUNTER')
    parser.add_argument('-a', '--alpha',       type=float, dest='TRIANGLE_ALPHA')

    return parser.parse_args(namespace=default_settings)


if __name__ == "__main__":
    from settings.default_settings import C

    settings = parse_arguments(C)

    print(settings)
    print C

    main(C)
