# Subdivergence-Free-Trees
Code for counting subdivergence-free gluings of arbitrary pairs of rooted trees.
Developed as part of an upcoming paper written in collaboration with Karen Yeats and Clair Xinle Dai. 
The abstract of the paper is as follows:

A gluing of two rooted trees is an identification of their leaves and un-subdivision of the resultant 2-valent vertices. A gluing of two rooted trees is subdivergence-free if it has no 2-edge cuts with both roots on the same side of the cut. The problem and language are motivated by quantum field theory. We enumerate subdivergence-free gluings for certain families of trees, showing a connection with connected permutations, and we give algorithms to compute subdivergence-free gluings.

subfreegluings.py contains an implementation of the second algorithm in the paper.

connectedperms.py contains code for computing S-connected permutations.


All code is written in Python 3. Install necessary modules by running:
```pip install -r requirements.txt```
