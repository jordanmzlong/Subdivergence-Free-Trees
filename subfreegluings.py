from itertools import chain, combinations, product
import copy
from functools import reduce
from multiset import Multiset
from collections import defaultdict, Counter

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
    # testing lopsided double line family formula
    k = 1
    n = 2
    while True:
        k = 1
        while k < n:
            l = n-k
            tbasic1 = Node([],[1])
            tbasic2 = Node([],[1])
            for i in range(1,k):
                tbasic1 = Node([tbasic1],[1])
            for i in range(1,l):
                tbasic2 = Node([tbasic2],[1])
            tdouble = Node([tbasic1,tbasic2],[])
            print(k, l, tdouble)
            print(subfree(tdouble,tdouble))
            k += 1
        n += 1

    """
    # testing double line family
    k = 1
    tbasic = Node([],[1])
    while True:
        tdouble = Node([tbasic,tbasic],[])
        print(k, tdouble)
        print(subfree(tdouble,tdouble))
        tbasic = Node([tbasic],[1])
        k += 1
    """
    """
    # testing remove_two_valent
    print(remove_two_valent(Node([],[1])))
    print(remove_two_valent(Node([Node([],[1])],[])))
    print(remove_two_valent(Node([Node([Node([],[1])],[])],[])))
    print(remove_two_valent(Node([Node([],[1]),Node([],[1])],[])))
    print(remove_two_valent(Node([Node([Node([],[1])],[])],[1])))
    """
    """
    root = Node([Node([],[1]), Node([],[1])],[1])
    tree = Tree(root)
    print(root)
    assert(count_sibling_subsets(tree.root) == 3)
    r1 = Node([Node([Node([Node([],[1])],[2])],[3])],[4])
    r2 = Node([Node([Node([Node([],[1])],[2])],[3]), Node([],[5])],[4])
    assert(count_sibling_subsets(r1) == 3)
    assert(count_sibling_subsets(r2) == 7)
    print(c(root))
    print(c(r1))
    print(c(r2))
    assert(Multiset([1,2,3,4,5]) == c(r2))
    for i in Multiset([1,1,1,2,3]).items():
        print(i)
    assert(colour_preserving(Multiset([1,1,1,2,3])) == 6)
    assert(fact(0) == 1)
    assert(fact(1) == 1)
    assert(fact(4) == 24)
    basic_root = Node([],[1])
    #print(deconstruct(basic_root))
    #print(deconstruct(root))
    #print(multiset_to_leaf)
    #print(subfree(root, root))
    """ 
    """
    # deconstruct tests
    t1 = Node([],[1])
    assert(subfree(t1,t1) == 1)
    assert(subs(t1,t1) == 0)
    t2 = Node([t1],[1])
    assert(subfree(t2,t2) == 1)
    assert(subs(t2,t2) == 1)
    t3 = Node([t2],[1])
    assert(subfree(t3,t3) == 3)
    t4 = Node([t3],[1])
    assert(subfree(t4,t4) == 13)
    t5 = Node([t4],[1])
    assert(subfree(t5,t5) == 71)
    tn = t5
    n = 5
    # got up to 14 without it getting too slow
    """
    """
    while True:
        n += 1
        print("round number",n)
        tn = Node([tn],[1])
        print(subfree(tn,tn))
    """
    """
    d0 = Node([],[1,1])
    #assert(subfree(d0,d0) == 2)
    d1 = Node([d0,d0],[])
    #print(d1)
    #print(deconstruct(d1))
    #print(subfree(d1,d1))
    #print(subs(d1,d1))
    assert(subfree(d1,d1) == 16)
    d2 = Node([d0],[1])
    d3 = Node([d2,d2],[])
    assert(subfree(d3,d3) == 512)
    d4 = Node([d2],[1])
    d5 = Node([d4,d4],[])
    assert(subfree(d5,d5) == 32576)
    # testing time... to test:
    # single tree family (DONE)
    # double tree family (DONE)
    # clair family
    # full family
    # perhaps a family with more children?
    d6 = Node([d0,d1],[])
    assert(subfree(d6,d6) == 384)
    d7 = Node([d0,d2],[])
    assert(subfree(d7,d7) == 80)
    d8 = Node([d0,d4],[])
    assert(subfree(d8,d8) == 528)
    d9 = Node([d2,d4],[])
    assert(subfree(d9,d9) == 3840)
    d10 = Node([d1,d1],[])
    assert(subfree(d10,d10) == 22528)
    
    d11 = Node([t1,t1], [])
    assert(subfree(d11,d11) == 0)
    d12 = Node([t2,t2],[])
    print(subfree(d12, d12))
    """
    """
    # testing Clair's family by creating t_{k,i} for every possible combination
    # Note the formula in the paper only applies when 1 < i < k
    k = 1
    i = 1
    while True:
        i = 1
        while i <= k:
            if i == 1:
                tsofar = Node([Node([],[1])],[])
            else:
                tsofar = Node([],[1])
            kcounter = k-1
            icounter = i-1
            while kcounter > 0:
                if icounter == 1:
                    tsofar = Node([tsofar, Node([],[1])],[])
                else:
                    tsofar = Node([tsofar],[1])
                icounter -= 1
                kcounter -= 1
            print(k,i,tsofar)
            print(subfree_wrapper(tsofar,tsofar))
            i += 1
        k += 1
    """


if __name__ == "__main__":
    main()
