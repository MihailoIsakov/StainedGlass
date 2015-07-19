<h1>Stained Glass is an image polygonization tool</h1> 
It uses simulated annealing to find an optimal image configuration for a given number of points.

The algorithm takes in two parameters, the image, and a heuristic image which specifies on which parts the annealing should focus on.

The image below is generated with: 
<code> ./main.py images/lion.jpg images/fcs_lion.jpg -t 20 -m 0.99 -n 300 -a 1 -p 0.9 </code>

Input image: <br>
![alt tag](https://github.com/ZiegHailo/StainedGlass/blob/master/images/lion.jpg?raw=true) <br>
Heuristic: <br>
![alt tag](https://github.com/ZiegHailo/StainedGlass/blob/master/images/fcs_lion.jpg?raw=true) <br>

Result: <br>
![alt tag](https://github.com/ZiegHailo/StainedGlass/blob/master/results/lion2.jpg?raw=true)
