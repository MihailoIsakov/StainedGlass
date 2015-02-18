__author__ = 'zieghailo'

import matplotlib.pyplot as plt
import matplotlib.pylab as pyl
import numpy as np

imagePlot = None
errorPlot = None

def start(size=(20, 10)):
    global imagePlot, errorPlot
    fig = plt.figure(1, figsize = size)
    imagePlot = fig.add_subplot(111)
    errorPlot = plt.figure(2).add_subplot(111)

    fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)
    plt.ion()
    plt.show()


def plot_mesh_collection(collection):
    # ax.clear()
    imagePlot.add_collection(collection)
    imagePlot.autoscale_view()
    imagePlot.axis('equal')
    plt.figure(1)
    plt.draw()


def plot_original(img, alpha):
    plt.figure(1)
    plt.imshow(img, alpha=alpha)


# def draw_mesh(mesh):
#     global imagePlot
#     mesh.build_collection()
#     pcol = mesh.collection
#     pcol.set_linewidth(0)
#     pcol.set_color(mesh.colors)
#     imagePlot.add_collection(pcol)
#     imagePlot.autoscale_view()
#     imagePlot.axis('equal')
#     plt.draw()
#     return imagePlot

oldx = None
oldy = None
def plot_points(mesh):
    global oldx, oldy, imagePlot
    x = [p.x for p in mesh.points]
    y = [p.y for p in mesh.points]
    imagePlot.clear()
    for p in mesh.points:
        imagePlot.plot(x, y, 'ro')
    if (oldx is not None):
        imagePlot.plot(oldx, oldy, 'bo')
    oldx = x
    oldy = y


def plot_arrow(mesh):
    global imagePlot
    # imagePlot.clear()
    STACK_SIZE = 10
    for p in mesh.points:
        p.past_positions.append([p.x, p.y])
        if len(p.past_positions) > STACK_SIZE:
            p.past_positions.popleft()

        if len(p.past_positions) > 2:
            pos = p.past_positions
            for i in range(min(STACK_SIZE - 1, len(p.past_positions) -1)):
                c = i * 1.0 / STACK_SIZE
            imagePlot.arrow(pos[i][0], pos[i][1],
                            pos[i+1][0] - pos[i][0], pos[i+1][1] - pos[i][1],
                            head_width=0.5, head_length=0.5, fc=(c,c,c), ec=(c,c,c))


errors = []
def plot_global_errors(error):
    global errorPlot, errors
    errors.append(error)
    errorPlot.plot(errors, 'r')
    plt.figure(2)
    # plt.ylim(0)
    plt.draw()


def keep_plot_open():
    plt.show()
    plt.waitforbuttonpress(0)


def plot_matrix(mat):
    plt.matshow(mat)
    plt.show()


def plot_error_hist(perr, trerr):
    pyl.figure(3)
    pyl.clf()
    n, bins, patches = pyl.hist([perr, trerr], 25, histtype='bar', stacked=False, fill=True,
                            color=['crimson', 'blue', ],
                            label=['Point errors', 'Triangle errors'])
    pyl.legend()
    pyl.draw()