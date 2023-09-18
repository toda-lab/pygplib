from pysat.formula import CNF
from pysat.solvers import Solver

from pygplib import Fo, NameMgr, GrSt, Prop
from examples.bmc import Bmc


def test_bmc():
    NameMgr.clear()
    N = 7
    E = [[0, 1,2,3,4,5,6,7],\
        [1]+[0,1,1,0,0,0,0], \
        [2]+[1,0,0,1,1,0,0], \
        [3]+[1,0,0,0,0,1,0], \
        [4]+[0,1,0,0,0,0,1], \
        [5]+[0,1,0,0,0,0,1], \
        [6]+[0,0,1,0,0,0,0], \
        [7]+[0,0,0,1,1,0,0], \
        ]
    dom = ((1,2), (2,3,4), (1,5), (3,6), (4,7), (5,), (6,7))
    Fo.st = GrSt(dom)

    state_expr = Fo.read(\
                    "    (! x1=x2 & ! edg(x1,x2)) "\
                    + "& (! x1=x3 & ! edg(x1,x3)) "\
                    + "& (! x2=x3 & ! edg(x2,x3)) "\
                    )
    trans_expr = None

    tests = (\
                ((3,4,5), (2,7,6), "TJ", "SAT"),\
                ((4,3,5), (6,7,2), "TJ", "SAT"),\
                ((3,4,5), (2,7,6), "TS", "UNSAT"),\
                ((2,7,3), (1,4,6), "TJ", "SAT"),\
                ((2,6,7), (2,7,6), "TS", "UNSAT"),\
            )

    for test_ini, test_fin, test_trans, expected in tests:
        ini_expr  = Fo.read(\
                          f"  x1=V{test_ini[0]} " \
                        + f"& x2=V{test_ini[1]} " \
                        + f"& x3=V{test_ini[2]} " \
                        )
        fin_expr = Fo.read(\
                          f"  x1=V{test_fin[0]} " \
                        + f"& x2=V{test_fin[1]} " \
                        + f"& x3=V{test_fin[2]} " \
                        )

        bmc = Bmc(state_expr, trans_expr, ini_expr, fin_expr,\
                    trans_type=test_trans)

        assert bmc._nof_free_vars == len(bmc._next_vars)

        for i in range(bmc._nof_free_vars):
            v = bmc._curr_vars[i]
            w = bmc._next_vars[i]
            assert bmc._varloc[v] == i
            assert bmc._varloc[w] == i

        for v in bmc._curr_vars:
            i = bmc._varloc[v]
            assert bmc._curr_vars[i] == v

        for w in bmc._next_vars:
            i = bmc._varloc[w]
            assert bmc._next_vars[i] == w

        solved = False
        for step in range(10):
            bmc.generate_cnf(step)

            cnf = CNF(from_clauses=bmc.cnf)
            with Solver(bootstrap_with=cnf) as solver:
                if solver.solve():
                    m = solver.get_model()
                else:
                    continue
            ans = []
            for assign in bmc.decode(m):
                res = Fo.st.get_interpretation_of_assign(assign)
                ans.append([res[key] + 1 for key in sorted(res.keys())])
            validate_ans(ans,N,E,test_ini,test_fin, test_trans)
            solved = True
            assert expected == "SAT"
            break

        assert solved or expected == "UNSAT"


def validate_ans(ans, n, E, ini, fin, trans_type):
    assert sorted(ans[0])  == sorted(ini)
    assert sorted(ans[-1]) == sorted(fin)

    prev = ()
    for curr in ans:
        for v in curr:
            for w in curr:
                assert E[abs(v)][abs(w)] == 0, \
                            f"E[{abs(v)}][{abs(w)}], curr={curr}"

        if prev != ():
            v = tuple(set(curr)-set(prev))
            w = tuple(set(prev)-set(curr))
            assert len(v) == 1
            assert len(w) == 1
            if trans_type == "TS":
                assert E[abs(v[0])][abs(w[0])] == 1

        prev = curr
