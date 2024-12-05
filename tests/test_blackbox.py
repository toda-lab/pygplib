from pygplib import Cnf, Prop, NameMgr, op, Fog, GrSt

from pysat.formula import CNF
from pysat.solvers import Solver


def test_solving_fog_in_fixed_graph():
    tests = [
        # independent set
        ("~x1=x2 & ~x1=x3 & ~x2=x3 & ~edg(x1,x2) & ~edg(x1,x3) & ~edg(x2,x3)", True),
        # independent set
        ("~x1=x2 & ~x1=x3 & ~x1=x4 & ~x1=x5 & ~x2=x3 & ~x2=x4 & ~x2=x5 & ~x3=x4 & ~x3=x5 & ~x4=x5 & ~edg(x1,x2) & ~edg(x1,x3)  & ~edg(x1,x4) & ~edg(x1,x5) & ~edg(x2,x3) & ~edg(x2,x4) & ~edg(x2,x5) & ~edg(x3,x4) & ~edg(x3,x5) & ~edg(x4,x5)", False),
        # clique
        ("~x1=x2 & ~x1=x3 & ~x2=x3 & edg(x1,x2)  & edg(x1,x3)  & edg(x2,x3)", False),
        # path
        ("~x1=x2 & ~x1=x3 & ~x1=x4 & ~x2=x3 & ~x2=x4 & ~x3=x4 & edg(x1,x2)  & edg(x2,x3)  & edg(x3,x4)", True),
        # cycle
        ("~x1=x2 & ~x1=x3 & ~x1=x4 & ~x2=x3 & ~x2=x4 & ~x3=x4 & edg(x1,x2)  & edg(x2,x3)  & edg(x3,x4) & edg(x4,x1)", True),
        # star 
        ("~x1=x2 & ~x1=x3 & ~x1=x4 & ~x2=x3 & ~x2=x4 & ~x3=x4 & edg(x1,x2)  & edg(x1,x3)  & edg(x1,x4)", True),
    ]
    NameMgr.clear()
    #
    # V1 ------- V3
    # |          |
    # |          |
    # V2---V5    |
    # |    |     |
    # |    |     |
    # V4---V7   V6
    #
    vertex_list = [1,2,3,4,5,6,7]                            # vertices of G
    edge_list = [(1,2),(1,3),(2,4),(2,5),(3,6),(4,7),(5,7)]  # edges of G

    for test_str, expected in tests:
        f = Fog.read(test_str)
        for encoding in ["direct", "log", "vertex", "edge", "clique"]:
            st = GrSt(vertex_list, edge_list, encoding=encoding)
            #assert False, f"{st._codes}"
            li  = []
            li.append(op.perform_boolean_encoding(f, st))
            li.append(st.compute_auxiliary_constraint(f))
            li += [st.compute_domain_constraint(v) \
                        for v in op.get_free_vars(f)]
            g = Prop.binop_batch(Prop.get_land_tag(), li)
            op._check_no_missing_variable_in_prop(g, st)
            mgr = Cnf(li, st=st, check_cnf=True)
            op._check_no_missing_variable_in_cnf(mgr._orig_cnf, st)
            with Solver(bootstrap_with=CNF(from_clauses=mgr.cnf)) as solver:
                solvable = solver.solve()
                if solvable:
                    ext_assign = solver.get_model()
                    assert len(ext_assign) == mgr.nvar
                    int_assign = mgr.decode_assignment(ext_assign)
                    op._check_no_missing_variable_in_assign(int_assign, st)
                    fo_assign = st.decode_assignment(int_assign)
                    ans = [st.object_to_vertex(fo_assign[key]) \
                                for key in fo_assign.keys()]
                assert solvable == expected, f"encoding={encoding},test_str={test_str}"
