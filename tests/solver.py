from pysat.formula import CNF
from pysat.solvers import Solver
from pyunigen import Sampler

from pygplib import Prop, NameMgr
import pygplib.op as op


def assert_satisfiable(f: Prop, msg: str = ""):
    assert not f.is_false_atom()
    if f.is_true_atom():
        return
    base, naux, cnf = op.compute_cnf((f,))
    with Solver(bootstrap_with=CNF(from_clauses=cnf)) as solver:
        assert solver.solve(), msg

def assert_unsatisfiable(f: Prop, msg: str = ""):
    assert not f.is_true_atom()
    if f.is_false_atom():
        return
    base, naux, cnf = op.compute_cnf((f,))
    with Solver(bootstrap_with=CNF(from_clauses=cnf)) as solver:
        assert not solver.solve(), msg

def assert_equivalence(f: Prop, g: Prop, msg: str = ""):
    assert_unsatisfiable(Prop.iff(f, Prop.neg(g)), msg=msg)
