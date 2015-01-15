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
    ax = plotter.start()
    ax = plotter.plot_mesh_collection(col, ax)

    past = time()
    now = 0
    while True:
        mesh.evolve(maxerr=20000, minerr=50000)

        now = time()
        print(now - past)
        past = now
        col = FlatMeshCollection(mesh)
        ax = plotter.plot_mesh_collection(col, ax)
        plotter.plot_points(mesh, ax)
        plotter.plot_arrow(mesh, ax)

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()
