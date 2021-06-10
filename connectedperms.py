def fact(n):
    sofar = 1
    for i in range(1,n+1):
        sofar *= i
    return sofar

def setsubtract(S,i):
    return {j - i for j in S}

def sconnected(n, S):
    total = 0
    for i in S:
        prefix = fact(i)#sconnected(i, {j for j in range(1,i)} - S)
        suffix = sconnected(n-i,{j for j in range(1,n-i)} & setsubtract(S,i))
        total += prefix*suffix
    #print("c", n, S, " = ", fact(n) - total)
    return fact(n) - total

def c(n):
    return sconnected(n,{i for i in range(1,n)})

import itertools
def genperms(n):
    plist = list(itertools.permutations([i+1 for i in range(n)]))
    return plist

def clair(k,i):
    if k < i:
        return 0
    if i == k:
        return c(k) - 2*sconnected(k-1,{j for j in range(i-1,k-1)}) + sconnected(k-2,{j for j in range(i-2,k-2)})
    if i == 1:
        return c(k)
    if i < k:
        return c(k) - 2*sconnected(k-1,{j for j in range(i-1,k-1)}) + sconnected(k-2,{j for j in range(i-2,k-2)}) - c(k-1)

def main():
    print(sconnected(5, {2,4}))
    print(c(5)+c(4)+c(2)*(c(3)+c(2)))
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
    # double tree family
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
    # clair family
    print(clair(3,2))
    k = 1
    while True:
        i = 1
        while i <= k:
            print(k, i, clair(k,i))
            i += 1
        k += 1
    """
#    total = 0
#    for i in genperms(6):
#        if (set([i[0],i[1]]) == {1,2} or (set([i[0],i[1],i[2]]) == {1,2,3} or set([i[0],i[1],i[2],i[3],i[4]]) == {1,2,3,4,5})):
#            total += 1
#    print(total)

if __name__ == "__main__":
    main()
