import random

from pysat.formula import CNF
from pysat.solvers import Solver

from pygplib import Prop, NameMgr, GrSt
import pygplib.op as op
from . import solver


def test_read():
    tests = [
        ("T", "T"),
        (" T", "T"),
        ("T ", "T"),
        ("~T", "(~ T)"),
        ("~ T", "(~ T)"),
        ("F", "F"),
        (" F", "F"),
        ("F ", "F"),
        ("~F", "(~ F)"),
        ("~ F", "(~ F)"),
        ("x_1", "x_1"),
        ("~x_1", "(~ x_1)"),
        ("~~T", "(~ (~ T))"),
        ("~(~T)", "(~ (~ T))"),
        ("((T))", "T"),
        ("T | T", "(T | T)"),
        ("T|T", "(T | T)"),
        ("T| T", "(T | T)"),
        ("T| T", "(T | T)"),
        ("T |T", "(T | T)"),
        ("(T|T)", "(T | T)"),
        ("(T)|T", "(T | T)"),
        ("T | T | T", "((T | T) | T)"),
        ("~T|T", "((~ T) | T)"),
        ("T|~T", "(T | (~ T))"),
        ("~(T|T)", "(~ (T | T))"),
        ("T & T | T", "((T & T) | T)"),
        ("T | T & T", "(T | (T & T))"),
        ("T->T", "(T -> T)"),
        ("T<->T", "(T <-> T)"),
        ("T | T -> T", "((T | T) -> T)"),
        ("T -> T | T", "(T -> (T | T))"),
        ("T -> T -> T", "((T -> T) -> T)"),
        ("T -> T <-> T", "((T -> T) <-> T)"),
        ("T <-> T -> T", "(T <-> (T -> T))"),
    ]

    NameMgr.clear()

    for test_str, expected in tests:
        res = Prop.read(test_str)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

def gen_form_rand(depth: int = 3) -> Prop:
    if depth < 1:
        raise ValueError("depth >= 1")

    def gen_atom_rand() -> Prop:
        var_name = ["x_1", "y_1", "z_1"]
        op = NameMgr.lookup_index(random.choice(var_name))

        atom_name = ["var", "T", "F"]
        name = random.choice(atom_name)
    pass

def gen_form_rand(depth: int = 3) -> Prop:
    if depth < 1:
        raise ValueError("depth >= 1")

    def gen_atom_rand() -> Prop:
        var_name = ["x_1", "y_1", "z_1"]
        op = NameMgr.lookup_index(random.choice(var_name))

        atom_name = ["var", "T", "F"]
        name = random.choice(atom_name)
        if name == "var":
            return Prop.var(op)
        if name == "T":
            return Prop.true_const()
        if name == "F":
            return Prop.false_const()
        assert False

    op_tag = [
        Prop.get_neg_tag(),
        Prop.get_land_tag(),
        Prop.get_lor_tag(),
        Prop.get_implies_tag(),
        Prop.get_iff_tag(),
        "NA",
    ]
    tag = random.choice(op_tag)

    if depth == 1 or tag == "NA":
        return gen_atom_rand()

    if tag == Prop.get_neg_tag():
        left = gen_form_rand(depth - 1)
        return Prop.neg(left)

    if (
        tag == Prop.get_land_tag()
        or tag == Prop.get_lor_tag()
        or tag == Prop.get_implies_tag()
        or tag == Prop.get_iff_tag()
    ):

        left = gen_form_rand(depth - 1)
        right = gen_form_rand(depth - 1)
        return Prop.binop(tag, left, right)
    assert False


def test_format():
    NameMgr.clear()

    for x in range(3):
        test_form = gen_form_rand()
        form_str = op.to_str(test_form)
        res_form = Prop.read(form_str)
        assert test_form == res_form


def test_compute_cnf():
    tests = [
        # formula,             its cnf
        ("~ (x & y -> z) | x", "x & (x | y) & (x | ~z)"),
        ("(x<->z) & ~y | x",   "(x | ~z) & (x | ~y)"),
        ("~(x<->~z) & ~y",   "(~x | y | z) & (x | ~y | z) & (x | y |~z) & (~x | ~y | z) & (x | ~y | ~z) & (~x | ~y | ~z)"),
    ]
    NameMgr.clear()

    for formula, expected in tests:
        f  = Prop.read(formula)
        g  = Prop.read(expected)
        solver.assert_equivalence(f,g)

def test_size():
    tests = [
        ("T", 1),
        ("~T", 2),
        ("~F", 2),
        ("x_1", 1),
        ("~x_1", 2),
        ("~~T", 3),
        ("((x1))", 1),
        ("x | y", 3),
        ("x | x", 3),
        ("~(x|~y|x)", 7),
    ]

    NameMgr.clear()

    for test_str, expected in tests:
        res = Prop.read(test_str)
        res_size = op.compute_size(res)
        assert res_size == expected, f"{op.to_str(res)}, {res_size}, {expected}"
