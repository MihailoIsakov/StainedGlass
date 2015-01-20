#! /usr/bin/env python

__author__ = 'zieghailo'

from mesh import Mesh
from support.meshcollection import FlatMeshCollection
import numpy as np
from time import time

def main():
    from support import plotter

    print("Running mesh.py")

    global mesh
    import cv2
    img = cv2.imread('images/lion.jpg')
    img = np.flipud(img)

    mesh = Mesh(img, 1000)

    print "Triangulating."
    mesh.delaunay()
    print "Coloring."
    mesh.colorize_stack()
    mesh.update_errors()

    col = FlatMeshCollection(mesh)
    plotter.start()
    plotter.plot_mesh_collection(col)

    past = time()
    now = 0
    while True:
        mesh.evolve(maxerr=20000, minerr=50000)

        now = time()
        print(now - past)
        past = now
        col = FlatMeshCollection(mesh)
        plotter.plot_mesh_collection(col)
        plotter.plot_points(mesh)
        plotter.plot_arrow(mesh)

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()
