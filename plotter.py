__author__ = 'zieghailo'

import matplotlib.pyplot as plt

def plot_mesh(mesh, size = (10,10)):
    fig, ax = plt.subplots()

    mesh.build_collection()
    pcol = mesh.collection
    pcol.set_linewidth(0)
    pcol.set_color(mesh.colors)
    ax.add_collection(pcol)
    ax.autoscale_view()
    ax.axis('equal')
    # plt.ion()
    plt.show()
    # plt.waitforbuttonpress(0)

