import random

from pygplib import Prop, NameMgr, GrSt
import pygplib.op as op


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
        ("x@1", "x@1"),
        ("~x@1", "(~ x@1)"),
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
        var_name = ["x@1", "y@1", "z@1"]
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
        (("T",), (0, set())),
        (("~ F",), (0, set())),
        (("F",), (0, {""})),
        (("~ T",), (0, {""})),
        (("x@1",), (1, {"1"})),
        # f2 <-> -f1      = (-f2 + (-f1)) * (f2 + f1)
        (("(~ x@1)",), (1, {"2", "-2,-1", "1,2"})),
        # f3 <-> f2 * f1   = ((-f3) + f1) * ((-f3) + f2) * (f3 + (-f1) + (-f2))
        (("x@1 & x@2",), (2, {"3", "-3,1", "-3,2", "-2,-1,3"})),
        # f3 <-> f1 + f2   = ((-f3) + f1 + f2) * (f3 + (-f1)) * (f3 + (-f2))
        (("x@1 | x@2",), (2, {"3", "-3,1,2", "-1,3", "-2,3"})),
        # f4 <-> f1 -> f2  = f4 <-> (f3 | f2) * (f3 <-> -f1)
        #                = ((-f4) + f3 + f2) * (f4 + (-f3)) * (f4 + (-f2))
        #                  * (f3 + f1) * ((-f3) + (-f1))
        (("x@1 -> x@2",), (2, {"4", "-4,2,3", "-3,4", "-2,4", "1,3", "-3,-1"})),
        (("T", "T"), (0, set())),
        (("T", "~ F"), (0, set())),
        (("F", "F"), (0, {""})),
        (("x@1", "x@2", "(~ x@1)"), (2, {"1", "2", "3", "-3,-1", "1,3"})),
    ]

    NameMgr.clear()

    for test_tup, expected in tests:
        res_tup = [Prop.read(test_str) for test_str in test_tup]
        base, naux, cnf = op.compute_cnf(tuple(res_tup))
        tab = [0] * (base + naux + 1)
        for cls in cnf:
            for lit in cls:
                assert abs(lit) <= base + naux
                tab[abs(lit)] = 1

        for i in range(1, naux + 1):
            assert (
                tab[base + i] == 1
            )  # all indices from base +1 to base+naux are used for aux vars.

        count = 0
        for i in range(1, base + 1):
            if tab[i] == 1:
                count += 1
        assert (
            count == expected[0]
        )  # some indices from 1 to base are used for propositional variables in test formula.

        # Renumber variable indices in order to compare with the expected result.
        new_index = 1
        for i in range(1, base + naux + 1):
            if tab[i] == 1:
                tab[i] = new_index
                new_index += 1

        # Normalize cnf as a set of strings.
        cnf_set = set()
        for cls in cnf:
            curr = set()
            for lit in cls:
                x = tab[abs(lit)]
                curr.add(x if lit > 0 else -x)
            cnf_set.add(",".join(map(str, sorted(curr))))

        assert cnf_set == expected[1], f"{cnf_set},  {expected[1]}"
