import tools.solver as solver
from pygplib import GrSt, Fo, NameMgr

def test_sample_vertexset():
    NameMgr.clear()
    N = 7 # number of vertices
    E = [[0, 1,2,3,4,5,6,7],\
        [1]+[0,1,1,0,0,0,0], \
        [2]+[1,0,0,1,1,0,0], \
        [3]+[1,0,0,0,0,1,0], \
        [4]+[0,1,0,0,0,0,1], \
        [5]+[0,1,0,0,0,0,1], \
        [6]+[0,0,1,0,0,0,0], \
        [7]+[0,0,0,1,1,0,0], \
        ] # E[v][w] = 1 iff v and w are adjacent.

    dom = ((1,2), (2,3,4), (1,5), (3,6), (4,7), (5,), (6,7))
    Fo.st = GrSt(dom)

    tests = (\
        ("(! x1=x2 & ! edg(x1,x2)) & (! x1=x3 & ! edg(x1,x3)) "\
                + "& (! x2=x3 & ! edg(x2,x3))", \
                is_independent_set),\
        ("A w (w=x1 | w=x2 | w=x3 | edg(w,x1) | edg(w,x2) | edg(w,x3))",\
                is_dominating_set),\
        #("A v (A w  (edg(v,w) -> (x1=v | x1=w | x2=v | x2=w | x3=v | x3=w)))",\
        #        is_vertex_cover),\
    )

    for formula_str, validator in tests:
        phi = Fo.read(formula_str)
        res = solver.sample_vertexset(phi, 5)
        for ans in res:
            validator(ans,N,E)


def is_independent_set(ans,N,E):
    for i in range(len(ans)):
        for j in range(i+1,len(ans)):
            v = ans[i][1]
            w = ans[j][1]
            assert 1 <= v and v <= N, f"{ans[i]}"
            assert 1 <= w and w <= N, f"{ans[j]}"

            assert v != w
            assert E[v][w] == 0


def is_dominating_set(ans,N,E):
    for w in range(1, N+1):
        found = False
        for i in range(len(ans)):
            v = ans[i][1]
            if v == w:
                found = True
            if E[v][w] == 1:
                found = True
        assert found, f"no vertex is equal to nor adjacent to {w}"


def is_vertex_cover(ans,N,E):
    for v in range(1, N+1):
        for w in range(1, N+1):
            if E[v][w] == 0:
                continue
            found = False
            for i in range(len(ans)):
                u = ans[i][1]
                if v == u:
                    found = True
                if w == u:
                    found = True
            assert found, f"edge ({v},{w}) is not covered by {ans[i]}"
