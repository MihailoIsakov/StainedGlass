__author__ = 'zieghailo'

import sys
import numpy as np
import plotter
from trimath import triangle_sum, rand_point_in_triangle, parallel_sum
from matplotlib.tri import Triangulation
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import multiprocessing


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
    def _get_ascending_order(triangles):
        """
        Create the order in which to sort the triangles,
        so that their values are ascending both horizontaly
        and vertically (but for not to disturb horizontaly)
        :param triangles: Nx3 numpy array
        :return: order in which to sort the triangles
        """
        # triangles = np.sort(triangles)
        order = np.lexsort((triangles[:, 2], triangles[:, 1], triangles[:, 0]))
        return order

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
        mapping = np.empty(newtr.shape[0])
        mapping[:] = np.nan
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
        order = self._get_ascending_order(self.triangles)
        self.triangles = self.triangles[order]
        self.colors = self.colors[order]
        self._triangle_errors = self._triangle_errors[order]

    @staticmethod
    def _sort_and_copy(triangles, *args):
        """
        For a triangles, a numpy array of Nx3, finds the order according to _sort_ascending,
        and returns sorted copies of triangles and any other arrays passed after it.
        :param triangles: numpy array of Nx3, defining triangle vertices
        :param args: any number of Nx3 numpy arrays
        :return: sorted arrays according to _sort_ascending
        """
        order = TriangleMesh._get_ascending_order(triangles)

        res_tr = np.copy(triangles)[order]
        res = [res_tr,]
        for a in args:
            res.append(np.copy(a)[order])

        return tuple(res)

    def generate_point(self, tri_ind):
        # sort the old points
        oldtriangles, oldcolors, olderrors = TriangleMesh._sort_and_copy(self.triangles, self.colors, self._triangle_errors)
        # add the point
        triangle = self.get_triangle(tri_ind)
        gen = rand_point_in_triangle(triangle)
        self._add_point(gen[0], gen[1])

        # get a new triangulation without the killed point
        # sort that too
        newtriangles = self._sort_and_copy(self.triangles)[0]
        self.triangles = newtriangles
        # a copy thats pointing to old points
        # set the colors for it to zeros
        self.colors = np.zeros([newtriangles.shape[0], 3])
        self._triangle_errors = np.zeros([newtriangles.shape[0]])

        mapping = TriangleMesh._map_triangles(oldtriangles, newtriangles)
        for new_i, mp in enumerate(mapping):
            if not np.isnan(mp):
                self.colors[new_i] = oldcolors[mp]
                self._triangle_errors[new_i] = olderrors[mp]
            else:
                input_triangle = self.get_triangle(new_i)
                self.colors[new_i], self._triangle_errors[new_i] = parallel_sum(self.img, input_triangle, True)



    def kill_point(self, kill):
        # sort the old points
        oldtriangles, oldcolors = self._get_ascending_order(self.triangles, self.colors)
        # kill the point
        self._remove_point(kill)

        # get a new triangulation without the killed point
        # sort that too
        newtriangles = self._get_ascending_order(self.triangles)
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

    def get_triangle(self, tri_index):
        return np.array([self.x[self.triangles[tri_index]], self.y[self.triangles[tri_index]]])

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

    def parallel_colorize(self, return_error=False):

        N = self.triangles.shape[0]
        self.colors = np.zeros([N, 3])
        self._triangle_errors = np.zeros([N])

        triangles = map(self.get_triangle, range(N))

        pool = multiprocessing.Pool(processes=8)
        import functools
        f = functools.partial(triangle_sum, self.img, get_error=return_error)

        res = pool.map(f, triangles)
        pool.close()
        pool.join()

        if not return_error:
            self.colors = np.array(res)
        else:
            # FIXME: too much array manipulation to get multiple params from sum_triangles
            res = np.array(res)
            self.colors = np.array([np.array(c[0]) for c in res])
            self._triangle_errors = np.array([np.array(c[1]) for c in res])


def main():
    np.seterr(all = 'ignore')

    print("Trimath main")
    import cv2
    img = cv2.imread('images/lion.jpg')

    img = np.flipud(img)

    print "Running Delaunay triangulation"
    dln = TriangleMesh(img, 5000)

    print "Caluclating triangle colors"
    dln.parallel_colorize(return_error=True)

    print "Plotting triangles"
    ax = plotter.start()
    ax = plotter.draw_mesh(dln, ax)

    for i in range(1000):
        # dln.get_point_errors()
        ind = np.argmax(dln._triangle_errors)
        dln.generate_point(ind)
        if i % 100 == 0:
            ax = plotter.draw_mesh(dln, ax)


    plotter.draw_mesh(dln, ax)
    print("Finished")

    plotter.keep_plot_open()

if __name__ == "__main__":
    main()



