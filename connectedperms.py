import itertools

# basic factorial function
def fact(n):
    sofar = 1
    for i in range(1,n+1):
        sofar *= i
    return sofar

# decrements each element of S by i
def setsubtract(S,i):
    return {j - i for j in S}

# returns the number of S-connected permutations of length n, where S is a set of integers
#   that is, permutations of length n that don't fix prefixes of sizes given in S
#   see paper for derivation
def sconnected(n, S):
    total = 0
    for i in S:
        prefix = fact(i)
        suffix = sconnected(n-i,{j for j in range(1,n-i)} & setsubtract(S,i))
        total += prefix*suffix
    return fact(n) - total

# returns the number of connected permutations of length n
#   that is, permutations of length n that don't fix any prefixes
def c(n):
    return sconnected(n,{i for i in range(1,n)})

# returns the number of subdivergence-free gluings of f_{k,i} in the paper
def third_family(k,i):
    if k < i:
        return 0
    if i == k:
        return c(k) - 2*sconnected(k-1,{j for j in range(i-1,k-1)}) + sconnected(k-2,{j for j in range(i-2,k-2)})
    if i == 1:
        return c(k)
    if i < k:
        return c(k) - 2*sconnected(k-1,{j for j in range(i-1,k-1)}) + sconnected(k-2,{j for j in range(i-2,k-2)}) - c(k-1)

def main():
    # basic example:
    assert(sconnected(5, {2,4}) == (c(5)+c(4)+c(2)*(c(3)+c(2))))

if __name__ == "__main__":
    main()