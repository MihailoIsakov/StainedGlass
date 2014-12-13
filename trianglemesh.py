__author__ = 'zieghailo'

import sys
import numpy as np
import plotter
from trimath import triangle_sum, rand_point_in_triangle
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

    def _add_point(self, x, y):
        """
        Adds a point and reruns the triangulation
        :param x: the x value of the point
        :param y: the y value of the point
        """
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)
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
        triangles = np.sort(triangles)
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
        o = 0  # old index
        n = 0  # new index
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

    def generate_point(self, tri_ind):
        # sort the old points
        oldtriangles, oldcolors = self._sort_ascending(self.triangles, self.colors)
        # add the point
        tri_vert = self.triangles[tri_ind]
        triangle = np.array([self.x[tri_vert], self.y[tri_vert]])
        gen = rand_point_in_triangle(triangle)
        self._add_point(gen[0], gen[1])

        # get a new triangulation without the killed point
        # sort that too
        newtriangles = self._sort_ascending(self.triangles)
        # a copy thats pointing to old points
        # set the colors for it to zeros
        self.colors = np.zeros([newtriangles.shape[0], 3])

        mapping = TriangleMesh._map_triangles(oldtriangles, newtriangles)
        for new_i, mp in enumerate(mapping):
            if not np.isnan(mp):
                self.colors[new_i] = oldcolors[mp]
            else:
                vertices = newtriangles[new_i]
                input_triangle = np.array([self.x[vertices], self.y[vertices]])
                self.colors[new_i], self._triangle_errors[new_i] = triangle_sum(self.img, input_triangle, True)

        self.triangles = newtriangles

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
        self.colors = np.zeros([newtriangles.shape[0], 3])

        mapping = TriangleMesh._map_triangles(oldtriangles, mutated)
        for new_i, mp in enumerate(mapping):
            if not np.isnan(mp):
                self.colors[new_i] = oldcolors[mp]
            else:
                vertices = newtriangles[new_i]
                input_triangle = np.array([self.x[vertices], self.y[vertices]])
                self.colors[new_i], self._triangle_errors[new_i] = triangle_sum(self.img, input_triangle, True)
                self.colors[new_i] = (0, 1, 0)

        self.triangles = newtriangles

    def get_point_errors(self):
        self._point_errors = np.zeros(self.x.shape[0])
        for tr_index, tr_vert in enumerate(self.triangles):
            tr_err = self._triangle_errors[tr_index]
            for vertex in tr_vert:
                self._point_errors[vertex] += tr_err

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

    def colorize(self, return_error=False):
        self.colors = np.zeros([self.triangles.shape[0], 3])
        self._triangle_errors = np.zeros([self.triangles.shape[0]])
        l = self.triangles.shape[0]

        for ind in range(l):
            sys.stdout.write('\r[' + '-' * (50 * ind / l) + ' ' * (50 - 50 * ind / l) + ']')
            triang = np.array([self.x[self.triangles[ind]], self.y[self.triangles[ind]]])
            self.colors[ind], self._triangle_errors[ind] = triangle_sum(self.img, triang, return_error)
        print ' '


def main():
    np.seterr(all = 'ignore')

    print("Trimath main")
    import cv2
    img = cv2.imread('images/lion.jpg')

    img = np.flipud(img)

    print "Running Delaunay triangulation"
    dln = TriangleMesh(img, 5000)

    print "Caluclating triangle colors"
    dln.colorize(return_error=True)

    print "Plotting triangles"
    ax = plotter.start()
    ax = plotter.draw_mesh(dln, ax)

    for i in range(1000):
        print i
        # dln.get_point_errors()
        minind = np.argmax(dln._triangle_errors)
        dln.generate_point(dln.triangles[minind])
        if i % 10 == 0:
            ax = plotter.draw_mesh(dln, ax)

    dln.colorize()

    plotter.draw_mesh(dln, ax)
    print("Finished")

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()



