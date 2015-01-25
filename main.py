#! /usr/bin/env python

__author__ = 'zieghailo'

from mesh import Mesh
import trimath
from support import plotter
from support.meshcollection import FlatMeshCollection

import cv2
import numpy as np
from time import time

def main():
    global mesh

    img = cv2.imread('images/renoir.jpg')
    img = np.flipud(img)
    trimath.set_image(img)

    mesh = Mesh(img, 1000)
    mesh.triangulate(True)

    col = FlatMeshCollection(mesh)
    plotter.start()
    plotter.plot_mesh_collection(col)
    past = time()

    pixtemp = 30  # pixels radius

    for cnt in range(10**6):
        print pixtemp
        purge = not bool(cnt % 50)
        if purge: print "Purging points"

        mesh.evolve(pixtemp, purge, maxerr=100000, minerr=500000, parallel=True)
        pixtemp *= 0.99

        now = time()
        print("Time elapsed: ", now - past)
        past = now
        plotter.plot_global_errors(mesh.error)

        if (cnt % 10 == 0):
            col = FlatMeshCollection(mesh)
            plotter.plot_mesh_collection(col)
            plotter.plot_arrow(mesh)

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()
