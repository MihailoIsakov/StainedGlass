__author__ = 'zieghailo'

import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt

def plot_triangles(dln, colors, size = (10,10)):
    fig, ax = plt.subplots()

    patches = []
    x = np.array(dln.x)
    y = np.array(dln.y)
    for tr in dln.triangles:
        polygon = Polygon(np.array([x[tr], y[tr]]).transpose())
        patches.append(polygon)

    pcol = PatchCollection(patches, True, alpha = 1)
    pcol.set_linewidth(0)
    pcol.set_color(colors)
    ax.add_collection(pcol)
    ax.autoscale_view()
    ax.axis('equal')
    plt.show()


if __name__ == "__main__":
    N = 1000
    from matplotlib.tri import Triangulation

    points = np.random.rand(N,2) * [10,20]
    dln = Triangulation(points[:, 0], points[:, 1])
    colors = tuple(np.random.rand(N,3))

    plot_triangles(dln, colors)
