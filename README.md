# sort

[sort](https://github.com/jarfo/sort) is a library for the study and optimization of comparators networks such as sorting networks, 
single-exception sorting networks and ϵ−halvers.

### Requirements
The code is written in __Python 3__ and requires [PyEDA](https://github.com/cjdrake/pyeda), which can be installed using pip
```
pip3 install pyeda
```

Pyeda includes the PicoSAT SAT solver. You can also use the [Glucose SAT solver](http://www.labri.fr/perso/lsimon/glucose/) or [Cryptominisat](https://github.com/msoos/cryptominisat). You may need to edit the path to these solvers in solver.py. 

### Usage

The software can be used to find sorting networks and other comparators networks using solver.py. 

### Examples

Joint size and depth optimization of sorting networks. 

* Optimal sorting network on 10 channels with 7 layers and 31 comparators (fixed maximal first layer as prefix)
```
$ python3 solver.py -n 10 -d 7 -s 31 --opt 'd' 
n: 10 d: 7 s: 31 opt: d solver: picosat
Elapsed: 13 s
[[(0, 9), (1, 8), (2, 7), (3, 6), (4, 5)], [(0, 1), (2, 4), (5, 7), (8, 9)], [(0, 2), (1, 6), (3, 8), (4, 5), (7, 9)], [(1, 4), (2, 3), (5, 8), (6, 7)], [(1, 2), (3, 5), (4, 6), (7, 8)], [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)], [(1, 2), (3, 4), (5, 6), (7, 8)]]
```

* Optimal sorting network on 10 channels with 7 layers and 31 comparators (no fixed prefix)
```
$ python3 solver.py -n 10 -d 7 -s 31 --opt 'd' --prefix []
n: 10 d: 7 s: 31 opt: d solver: picosat prefix: []
Elapsed: 300 s
[[(0, 9), (1, 5), (2, 6), (3, 8), (4, 7)], [(0, 4), (1, 8), (2, 5), (3, 6), (7, 9)], [(0, 2), (1, 4), (3, 7), (5, 6), (8, 9)], [(1, 3), (2, 8), (4, 6), (5, 7)], [(0, 1), (2, 3), (4, 5), (6, 9), (7, 8)], [(1, 2), (3, 4), (5, 7), (6, 8)], [(2, 3), (4, 5), (6, 7)]]
```

* Optimal 1/4-halver on 12 channels with 4 layers and 17 comparators
```
$ python3 solver.py -n 12 -d 4 -s 17 -e 0.25 --opt h --solver glucose
n: 12 d: 4 s: 17 opt: h solver: glucose
Elapsed: 877.27 s
[[(0, 4), (1, 2), (3, 9), (5, 10), (6, 11), (7, 8)], [(0, 6), (1, 3), (2, 8), (4, 7), (9, 11)], [(2, 5), (3, 4), (6, 10), (7, 9)], [(4, 6), (5, 7)]]
```

* Optimal single exception sorting network on 10 channels with 7 layers and 31 comparators
```
$ python3 solver.py -n 10 -d 7 -s 31 -u 1 --opt 'd1' --solver glucose
n: 10 d: 7 s: 31 u: 1 opt: d1 solver: glucose
Elapsed: 64.51 s
495 (0111101111) -> 383 (0101111111) Fails
[[(0, 3), (1, 7), (2, 6), (4, 9), (5, 8)], [(0, 5), (1, 4), (2, 9), (3, 8), (6, 7)], [(0, 1), (2, 5), (3, 9), (4, 6), (7, 8)], [(1, 2), (3, 4), (5, 6), (7, 9)], [(1, 3), (2, 5), (4, 7), (6, 9)], [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)], [(1, 2), (3, 4), (5, 6)]]
```

### Code used in the following papers:
* [Joint Size and Depth Optimization of Sorting Networks](https://arxiv.org/abs/1806.00305)
* [SAT encodings for sorting networks, single-exception sorting networks and ϵ−halvers](http://arxiv.org/abs/1807.05377)
