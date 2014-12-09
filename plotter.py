__author__ = 'zieghailo'

import matplotlib.pyplot as plt


def start(size = (20,10)):
    fig = plt.figure(figsize = size)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)
    plt.ion()
    plt.show()
    return ax


def draw_mesh(mesh, ax):
    import numpy
    x = numpy.random.rand()
    if x > 0.9:
        mesh.colors[int(numpy.random.rand() * 100)] = (0, 1, 0)
    mesh.build_collection()
    pcol = mesh.collection
    pcol.set_linewidth(0)
    pcol.set_color(mesh.colors)
    ax.add_collection(pcol)
    ax.autoscale_view()
    ax.axis('equal')
    plt.draw()
    return ax

def keep_plot_open():
    plt.show()
    plt.waitforbuttonpress(0)