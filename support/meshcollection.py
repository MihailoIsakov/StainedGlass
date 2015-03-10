__author__ = 'zieghailo'
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from collections import deque

from triangulation import nptriangle2result


class FlatMeshCollection(PatchCollection):
    """
    Like MeshCollection, but works with plain numpy arrays instead of Triangle objects
    """
    def __init__(self, mesh, alpha=1):
        patches = deque()
        colors = deque()
        for tr in mesh.triangles:
            patches.append(Polygon(tr.transpose()))
            try:
                colors.append(nptriangle2result(tr)[0] + (alpha,))
            except KeyError:
                colors.append((0,1,0))

        PatchCollection.__init__(self, list(patches))
        self.set_color(list(colors))
        self.set_linewidth(0)


class FlatMeshErrorCollection(PatchCollection):
    """
    Same as FlatMeshCollection, but plots errors instead of colors.
    """

    def __init__(self, mesh):
        patches = deque()
        colors = deque()

        max_err = 0
        for tr in mesh.triangles:
            patches.append(Polygon(tr.transpose()))
            try:
                err = nptriangle2result(tr)[1]
                max_err = max(err, max_err)
                colors.append(err)
            except KeyError:
                colors.append((0, 1, 0))

        colors = [(c/max_err, c/max_err, c/max_err) for c in colors]

        PatchCollection.__init__(self, list(patches))
        self.set_color(list(colors))
        self.set_linewidth(0)