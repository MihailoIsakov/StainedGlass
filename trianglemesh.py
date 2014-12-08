__author__ = 'zieghailo'

import sys
import numpy as np
import plotter
from trimath import triangle_sum
from matplotlib.tri import Triangulation
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


class TriangleMesh(Triangulation):
    img = None
    _patches = []
    collection = None
    colors = []
    _triangle_errors = []
    _point_errors = []


    def __init__(self, img, N):
        self.img = img
        self.randomize(N)

        Triangulation.__init__(self, self.x, self.y)


    def randomize(self, N):
        h,w = self.img.shape[:2]

        self.x = np.random.rand(N) * (w - 1)
        self.y = np.random.rand(N) * (h - 1)

        self.x[0:4] = [0, w-1, 0, w-1]
        self.y[0:4] = [0, 0, h-1, h-1]

        return (self.x, self.y)


    def _remove_point(self, kill):
        """
        Removes a point and reruns the triangulation
        :param kill: The index of the point to be killed
        """
        self.x = np.delete(self.x, kill)
        self.y = np.delete(self.y, kill)
        Triangulation.__init__(self, self.x, self.y)


    @staticmethod
    def _sort_ascending(triangles, colors = None):
        """
        Copy and sort the array both horizontally and vertically
        Horizontally by arranging the vertices in ascending order,
        and vertically by sorting the triangles by the _bigger comparison
        :param triangles: Nx3 numpy array
        :param colors: colors assigned to the triangles
        :return: copied sorted triangles
        """
        tr = np.sort(triangles)
        order = np.lexsort((triangles[:, 2], triangles[:, 1], triangles[:, 0]))
        if colors is None:
            return triangles[order]
        return triangles[order], colors[order]


    @staticmethod
    def _bigger(t1, t2):
        """
        Tests if a triangle should come before some other in the list
        :param t1: triangle 1
        :param t2: triangle 2
        :return: True if t1 should come after t2
        """
        bigger = True
        if t2[0] > t1[0]:
            bigger = False
        elif t2[0] == t1[0] and t2[1] > t1[1]:
            bigger = False
        elif t2[0] == t1[0] and t2[1] == t1[1] and t2[2] > t1[2]:
            bigger = False
        return bigger


    @staticmethod
    def _map_triangles(oldtr, newtr):
        """
        Creates a numpy array mapping the old triangles to the new ones
        :param oldtr: Old triangulation, should have more elements than the new one
        :param newtr: New triangulation.
        :return: Numpy array mapping the index of each old triangle to a new one.
        """
        o = 0 # old index
        n = 0 # new index
        mapping = np.zeros(newtr.shape[0])
        while n < newtr.shape[0] and o < oldtr.shape[0]:
            if (oldtr[o] == newtr[n]).all():
                # reuse the old color
                mapping[n] = o
                o += 1; n += 1
            elif TriangleMesh._bigger(newtr[n], oldtr[o]):
                # some triangle in newtr got tossed out, so we ignore the color
                o += 1
            elif TriangleMesh._bigger(oldtr[o], newtr[n]):
                mapping[n] = None
                n += 1
        return mapping


    def _sort_triangles(self):
        self.triangles, self.colors = self._sort_ascending(self.triangles, self.colors)


    def kill_point(self, kill):
        # sort the old points
        oldtriangles, oldcolors = self._sort_ascending(self.triangles, self.colors)
        # kill the point
        self._remove_point(kill)

        # get a new triangulation without the killed point
        # sort that too
        newtriangles = self._sort_ascending(self.triangles)
        # a copy thats pointing to old points
        mutated = np.copy(newtriangles)
        mutated[mutated >= kill] += 1
        # set the colors for it to zeros
        newcolors = np.zeros([newtriangles.shape[0], 3])

        mapping = TriangleMesh._map_triangles(oldtriangles, mutated)
        for new_i, mp in enumerate(mapping):
            if not np.isnan(mp):
                print mp
                ind = int(mp)
                newcolors[new_i] = oldcolors[mp]

        self.triangles = newtriangles
        self.colors = newcolors


    def add_point(self, x, y):
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)
        Triangulation.__init__(self, self.x, self.y)


    def build_collection(self):
        """
        Builds a collection of patches from the triangles and the points stored in the object.
        :return: returns the collection, also it is stored in the object.
        """
        #TODO: should the building be called before every plot?
        # We can optimize here, but it may be unnecessary
        self._patches = []
        for tr in self.triangles:
            self._patches.append(Polygon(np.array([self.x[tr], self.y[tr]]).transpose()))
        self.collection = PatchCollection(self._patches)
        return self.collection


    def colorize(self, return_error = False):
        self.colors = np.zeros([self.triangles.shape[0], 3])
        self.errors = np.zeros([self.triangles.shape[0]])
        l = self.triangles.shape[0]

        for ind in range(l):
            sys.stdout.write('\r[' + '-' * (50 * ind / l) + ' ' * (50 - 50 * ind / l) + ']')
            triang = np.array([self.x[self.triangles[ind]], self.y[self.triangles[ind]]])
            c, e  = triangle_sum(self.img, triang, return_error)
            self.colors[ind] = c
            self.errors[ind] = e

        print ' '


def main():
    np.seterr(all = 'ignore')

    print("Trimath main")
    import cv2
    img = cv2.imread('images/tara.jpg')

    img = np.flipud(img)

    print "Running Delaunay triangulation"
    dln = TriangleMesh(img, 500)

    print "Caluclating triangle colors"
    dln.colorize(return_error = True)

    print "Plotting triangles"
    plotter.plot_mesh(dln)

    count = 0
    for i in range (200):
        dln.kill_point(np.round(np.random.rand() * 200).astype(int))

    dln.colorize()

    plotter.plot_mesh(dln)
    print("Finished")


if __name__ == "__main__":
    main()



