"""Utility functions that require third-parity modules"""
from pysat.formula import CNF
from pysat.solvers import Solver

from pyunigen import Sampler

from pygplib import Fo, NameMgr
from pygplib import op

def solve_vertexset(expr: Fo):
    """Solve vertex-set, given first-order property.

    Args:
        expr: first-order formula of property of a vertex-set

    Returns
        tuple representings an assignment of first-order variables and
        it consists of pairs of variable names and vertex indices.
    """
    if Fo.st is None:
        raise Exception("Set graph structure of Fo class")

    prop_expr = op.propnize(expr)
    tup  = op.compute_domain_constraint(expr)
    base, naux, cnf = op.compute_cnf( (prop_expr, ) + tup )

    cnf = CNF(from_clauses=cnf)
    with Solver(bootstrap_with=cnf) as solver:
        if solver.solve():
            assign = solver.get_model()

    # Filter out all literals of auxilliary variables in CNF-encoding.
    assign = [lit for lit in assign if abs(lit) <= base]

    res = Fo.st.get_interpretation_of_assign(assign)
    decoded_assign = tuple([(NameMgr.lookup_name(key), res[key]+1) \
                        for key in sorted(res.keys())])
    return decoded_assign


def sample_vertexset(expr: Fo, num: int = 1):
    """Samples vertex-sets at random.

    Args:
        expr: first-order formula of property of a vertex-set
        num: number of samples

    Returns
        tuple of tuples, where each tuple representings an assignment of
        first-order variables and it consists of pairs of variable names and
        vertex indices.
    """
    if Fo.st is None:
        raise Exception("Set graph structure of Fo class")

    prop_expr = op.propnize(expr)
    tup  = op.compute_domain_constraint(expr)
    base, naux, cnf = op.compute_cnf( (prop_expr, ) + tup )

    c = Sampler()
    for clause in cnf:
        c.add_clause( list(clause) )

    cells, hashes, samples = c.sample(num, sampling_set=range(1,base+1))

    ans = []
    for assign in samples:
        res = Fo.st.get_interpretation_of_assign(assign)
        decoded_assign = tuple([(NameMgr.lookup_name(key), res[key]+1) \
                            for key in sorted(res.keys())])
        ans.append(decoded_assign)

    return tuple(ans)
