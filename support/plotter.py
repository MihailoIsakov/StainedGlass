__author__ = 'zieghailo'

import matplotlib.pyplot as plt


def start(size = (20,10)):
    fig = plt.figure(figsize = size)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)
    plt.ion()
    plt.show()
    return ax


def plot_mesh_collection(collection, ax):
    # ax.clear()
    ax.add_collection(collection)
    ax.autoscale_view()
    ax.axis('equal')
    plt.draw()
    return ax


def draw_mesh(mesh, ax):
    mesh.build_collection()
    pcol = mesh.collection
    pcol.set_linewidth(0)
    pcol.set_color(mesh.colors)
    ax.add_collection(pcol)
    ax.autoscale_view()
    ax.axis('equal')
    plt.draw()
    return ax

oldx = None
oldy = None
def plot_points(mesh, ax):
    global oldx, oldy
    x = [p.x for p in mesh.points]
    y = [p.y for p in mesh.points]
    ax.clear()
    for p in mesh.points:
        ax.plot(x, y, 'ro')
    if (oldx is not None):
        ax.plot(oldx, oldy, 'bo')
    oldx = x
    oldy = y


def plot_arrow(mesh, ax):
    ax.clear()
    STACK_SIZE = 10
    for p in mesh.points:
        p.past_positions.append([p.x, p.y])
        if len(p.past_positions) > STACK_SIZE:
            p.past_positions.popleft()

        if len(p.past_positions) > 2:
            pos = p.past_positions
            for i in range(min(STACK_SIZE - 1, len(p.past_positions) -1)):
                c = 1.0/(i+1.0)
                ax.arrow(pos[i][0], pos[i][1],
                         pos[i+1][0] - pos[i][0], pos[i+1][1] - pos[i][1],
                         head_width=0.5, head_length=0.5, fc=(c,c,c), ec=(c,c,c))


def keep_plot_open():
    plt.show()
    plt.waitforbuttonpress(0)