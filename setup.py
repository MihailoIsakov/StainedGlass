__author__ = 'zieghailo'

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "Stained Glass",
    ext_modules = cythonize('trimath.pyx'),
    requires=['numpy', 'xxhash']  # accepts a glob pattern
)