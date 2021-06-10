import copy
from collections import Counter, defaultdict
from functools import reduce
from itertools import chain, combinations, product

from multiset import Multiset

# used to generate new colour labels
leaf_counter = 1

# returns a list of all nonempty subsets (found on stack overflow)
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return list(chain.from_iterable(combinations(s,r) for r in range(1,len(s)+1)))

# children is a list of nodes, representing children of the node.
# half_edges is a list of numbers representing the half_edges with their colours
class Node:

    def __init__(self, children, half_edges):
        self.children = children
        self.half_edges = half_edges

    def __repr__(self):
        "the printing function"
        sofar = "["
        for half_edge in self.half_edges:
            sofar += str(half_edge)
        for child in self.children:
            sofar += repr(child)
        sofar += "]"
        return sofar

# given a node t, returns a multiset of all of the half-edge colours t
def c(t):
   leaves = []
   leaves += t.half_edges
   for child in t.children:
       leaves += c(child)
   return Multiset(leaves)

# your basic factorial function
def fact(n):
    sofar = 1
    for i in range(1,n+1):
        sofar *= i
    return sofar

# return the number of colour preserving gluings given a multiset of colours
def colour_preserving(colours):
    total = 1
    for (elt,multiplicity) in colours.items():
        total *= fact(multiplicity)
    return total

# our most important function!
# computes the number of subdivergence-free gluings of trees t1 and t2
def subfree(t1,t2):
    t1_colours = c(t1)
    if t1_colours != c(t2):
        return 0
    return colour_preserving(t1_colours) - subs(t1,t2)

# given a multiset of leaf labels called colours
# and a dictionary of leaf multisets to new leaf labels
# get the leaf label corresponding to colours
# Note: mutates multiset_to_leaf
def getlabel(colours, multiset_to_leaf):
    global leaf_counter
    found = False
    for (key,val) in multiset_to_leaf:
        if key == colours and found:
            print("ERROR IN RELABELING MULTISET, MULTIPLE KEYS")
        if key == colours and not found:
            edge_label = val
            found = True
    if not found:
        leaf_counter = leaf_counter + 1
        edge_label = leaf_counter
        multiset_to_leaf.append((colours, edge_label))
    return edge_label

# return a list with an entry for every subset of siblings in t
# of the form (base tree, colourlist)
# colourlist is a list of colour multisets, base tree is a coloured rooted tree
# multiset_to_leaf is the dictionary for generating half-edge labels of the base tree
def deconstruct(t, multiset_to_leaf):
    sofar = []
    children = copy.deepcopy(t.children)
    half_edges = copy.deepcopy(t.half_edges)
    for children_subset in powerset(children):
        # finding the multiset complement of children
        diff = Counter(children) - Counter(children_subset)
        leftover_children = list(diff.elements()) 
        # this is basically the same as below except when the descend subset is empty
        # need to copy since it's pass by reference by default, and we're mutating it
        base = Node(copy.deepcopy(leftover_children), copy.deepcopy(half_edges))
        colourlist = []
        for i in children_subset:
            icolours = c(i)
            colourlist.append(icolours)
            edge_label = getlabel(icolours, multiset_to_leaf)
            base.half_edges.append(edge_label)
        sofar += [(base,colourlist)]
        
        # the descend_subset is the subset of children that we'll recursively deconstruct
        for descend_subset in powerset(children_subset):
            # new_childrenish is a list of tuples to be added as children
            # we're taking the cross product of the results of deconstructing the children, in order
            #   to cover every possible set of siblings in the tree
            # NOTE that this might be a source of error, since you may have multiple threads trying
            #   to access the same multiset_to_leaf dictionary, but I assume python is able to take care
            #   of this
            new_childrenish = list(product(*map(lambda x: deconstruct(x, multiset_to_leaf), descend_subset)))
            # don't strictly need this check, but it might speed things up
            if new_childrenish == []:
                continue
            # finding set complement of the descend_subset
            diff = Counter(children_subset) - Counter(descend_subset)
            to_cut = list(diff.elements())
            base = Node(copy.deepcopy(leftover_children), copy.deepcopy(half_edges))
            colourlist = []
            # for the children we're not descending down but still cutting, we need to modify the half-edges
            for i in to_cut:
                icolours = c(i)
                colourlist.append(icolours)
                base.half_edges.append(getlabel(icolours, multiset_to_leaf))
            for tup in new_childrenish:
                # tup is a tuple of tuples, first element being the new child, second being the colours
                newcolourlist = copy.deepcopy(colourlist)
                newbase = copy.deepcopy(base)
                for (childtree,childcolourlist) in tup:
                    newbase.children.append(childtree)
                    newcolourlist += childcolourlist
                sofar += [(newbase,newcolourlist)]
    return sofar

# generates the number of gluings with subdivergences given trees t1 and t2
def subs(t1,t2):
    total = 0
    multiset_to_leaf = [] # this will be a list of (colour_multiset,label) tuples
    # need a new dictionary of these for every call
    for (base1, coloursets1) in deconstruct(t1, multiset_to_leaf):
        for (base2, coloursets2) in deconstruct(t2, multiset_to_leaf):
            basegluings = subfree(base1, base2)
            if basegluings < 0:
                print("ERROR: negative result from call to subfree")
            if basegluings:
                for colours in coloursets1:
                    basegluings *= colour_preserving(colours)
            total += basegluings
    return total

# count all of the subsets of siblings of this tree
def count_sibling_subsets(t):
    sofar = 0 
    for children_subset in powerset(t.children):
        subset_count = 1
        for i in children_subset:
            subset_count = subset_count*(1+count_sibling_subsets(i))
        sofar += subset_count
    return sofar

# removes internal two-valent vertices by contracting edges
# does not remove anything since we don't want to remove the 
#  edge after the root if the root has only one child
def remove_two_valent(t):
    return Node(list(map(remove_two_valent_helper, t.children)), t.half_edges)

def remove_two_valent_helper(t):
    if len(t.children) == 1 and t.half_edges == []:
        return remove_two_valent_helper(t.children[0])
    return Node(list(map(remove_two_valent_helper, t.children)), t.half_edges)

# if either tree might have two-valent vertices use this instead of subfree
def subfree_wrapper(t1,t2):
    t1 = remove_two_valent(t1)
    t2 = remove_two_valent(t2)
    return subfree(t1,t2)

def main():
    # some basic examples:
    t1 = Node([],[1])
    assert(subfree_wrapper(t1,t1) == 1)
    t2 = Node([t1],[1])
    assert(subfree_wrapper(t2,t2) == 1)
    t3 = Node([t2],[1])
    assert(subfree_wrapper(t3,t3) == 3)
    t4 = Node([t3],[1])
    assert(subfree_wrapper(t4,t4) == 13)
    t5 = Node([t4],[1])
    assert(subfree_wrapper(t5,t5) == 71)
    

if __name__ == "__main__":
    main()