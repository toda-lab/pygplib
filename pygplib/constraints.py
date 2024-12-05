from typing import Iterable

from .name     import NameMgr

def at_most_r(x: Iterable[int], r: int) -> str:
    """Computes at-most-r constraint of O.Bailleux and Y.Boufkhad.

    See also TAOCP Vol.4, Fascicle 6, p.8.

    Example:
        x1 + x2 + x3 <= 2
        Suppose that the indices of x1,x2,x3 are 1,2,3, respectively.
        > x = [1, 2, 3]
        > r = 2
        > at_most_r(x,r)
    """
    if len(x) == 0:
        raise Exception("No variable given")
    for i in x:
        if not NameMgr.has_name(i):
            raise Exception("found variable with no name.")
    x = (0,) + tuple(x)
    b_dict = {}

    def b(k: int, i: int) -> str:
        if i == 0:
            return "T"
        if i == r+1:
            return "F"
        if (k,i) not in b_dict:
            b_dict[(k,i)] = NameMgr.get_aux_index()
        return f"{NameMgr.lookup_name(b_dict[(k,i)])}"

    n = len(x)-1
    if r >= n:
        return "T"
    if r < 0:
        return "F"
    if r == 0:
        return " & ".join(["~"+NameMgr.lookup_name(x[i]) for i in range(1,len(x))])
    t = [0]*(2*n)
    for k in range(2*n-1,n-1,-1):
        t[k] = 1
        b_dict[(k,1)] = x[k-n+1]
    for k in range(n-1,0,-1):
        t[k] = min(r,t[2*k]+t[2*k+1])
    li = []
    for k in range(2,n):
        for i in range(t[2*k]+1):
            for j in range(t[2*k+1]+1):
                if not 1 <= i+j <= t[k]+1:
                    continue
                li.append(f"(~{b(2*k,i)} | ~{b(2*k+1,j)} | {b(k,i+j)})")
    for i in range(t[2]+1):
        for j in range(t[3]+1):
            if i+j != r+1:
                continue
            li.append(f"(~{b(2,i)} | ~{b(3,j)})")
    return " & ".join(li)
