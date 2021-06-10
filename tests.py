# Part 1: Testing general algorithm
    """
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
    """
    # testing symmetric double tree family
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
    # testing some helper functions
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
    # testing the basic line family
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
    while True:
        n += 1
        print("round number",n)
        tn = Node([tn],[1])
        print(subfree(tn,tn))
    """
    """
    # testing symmetric double tree family again
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
    # testing third tree family by creating t_{k,i} for every possible combination
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

# Part 2: Testing formulas
    """
    # double tree family via formula
    n = 2
    while True:
        k = 1
        while k < n:
            l = n-k
            print(k, l)
            total = fact(n)
            inside1 = fact(k)*fact(l)
            for i in range(1,k):
                for j in range(1,l):
                    inside1 += fact(i)*fact(j)*c(k+l-i-j)
            for i in range(1,k):
                inside1 += fact(i)*c(k+l-i)
            for j in range(1,l):
                inside1 += fact(j)*c(k+l-j)
            a = min(k,l)
            inside2 = 0
            for i in range(1,a+1):
                for j in range(1,a+1):
                    inside2 += fact(i)*fact(j)*sconnected(k+l-i-j,{m for m in range(1,a-i+1)} | {m for m in range(k+l-i-j-(a-j),k+l-i-j)})
            for i in range(1,a+1):
                inside2 += 2*fact(i)*sconnected(k+l-i,{m for m in range(1,a-i+1)} | {m for m in range(k+l-a-i,k+l-i)})
            print(total - inside1 - inside2)
            k += 1
        n += 1
    """
    """
    # symmetric double tree family with formula
    k = 1
    while True:
        total = fact(2*k)
        inside = fact(k)*fact(k)
        for i in range(1,k):
            for j in range(1,k):
                inside += fact(i)*fact(j)*c(2*k-i-j)
        for i in range(1,k):
            inside += 2*fact(i)*c(2*k-i)
        print(k)
        print(total - 2*inside)
        k += 1
    """
    """
    # third family
    print(third_family(3,2))
    k = 1
    while True:
        i = 1
        while i <= k:
            print(k, i, third_family(k,i))
            i += 1
        k += 1
    """