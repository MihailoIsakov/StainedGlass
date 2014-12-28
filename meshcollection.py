__author__ = 'zieghailo'
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

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