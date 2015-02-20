Stained Glass vectorizes an image so that it is composed of a number of monochrome triangles, while trying to minimize the errror. It uses simulated annealing to optimize the image quality, by moving the points around and measuring the error they are causing.

To run Stainged Glass with a default image, just pull the repo and run <code>./main.py </code>
While assigning images from the command line is planned, for now just change the settings file that is imported in the main.py file, and modify/create your own in the settings folder.

Stained Glass uses numpy, scipy, openCV, matplotlib, xxHash. (I may have forgotten a couple, I'll check soon)
