__author__ = 'zieghailo'
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from collections import deque

class MeshCollection(PatchCollection):

    def __init__(self, triangles, colors):
        # TODO polygon creation can be tied to triangle creation for optimization
        self._triangles = triangles
        self._colors = colors

        patches = []
        for tr in triangles:
            patches.append(Polygon(tr.flat_vertices.transpose()))

        PatchCollection.__init__(self, patches)
        self.set_color(colors)
        self.set_linewidth(0)


class FlatMeshCollection(PatchCollection):
    """
    Like MeshCollection, but works with plain numpy arrays instead of Triangle objects
    """
    def __init__(self, mesh):
        patches = deque()
        colors = deque()
        for tr in mesh.triangles:
            patches.append(Polygon(tr.transpose()))
            try:
                colors.append(mesh.get_result(tr)[0])
            except KeyError:
                colors.append((0,1,0))

        PatchCollection.__init__(self, list(patches))
        self.set_color(list(colors))
        self.set_linewidth(0)