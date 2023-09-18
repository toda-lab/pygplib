import random

from pygplib import Fo, NameMgr, GrSt, Prop
import pygplib.op as op

def test_read():
    tests = [
        ("T",   "T"),
        (" T",  "T"),
        ("T ",  "T"),
        ("!T",  "(! T)"),
        ("! T", "(! T)"),
        ("F",   "F"),
        (" F",  "F"),
        ("F ",  "F"),
        ("!F",  "(! F)"),
        ("! F", "(! F)"),
        ("x = x", "x = x"),
        ("y = x", "x = y"),
        ("x12 = x2",  "x12 = x2"),
        ("x12 = x02", "x02 = x12"),
        ("x = y", "x = y"),
        ("x=y",   "x = y"),
        ("(x=y)", "x = y"),
        ("!x=y",  "(! x = y)"),
        ("! x=y", "(! x = y)"),
        ("edg(x,x)",   "edg(x, x)"),
        ("(edg(x,x))", "edg(x, x)"),
        ("edg(y,x)",   "edg(x, y)"),
        ("edg(x,y)",   "edg(x, y)"),
        ("edg(x, y)",  "edg(x, y)"),
        ("edg (x, y)", "edg(x, y)"),
        ("edg(x,y )",  "edg(x, y)"),
        ("edg( x,y)",  "edg(x, y)"),
        ("!edg(x,y)",  "(! edg(x, y))"),
        ("! edg(x,y)", "(! edg(x, y))"),
        ("!!T",   "(! (! T))"),
        ("!(!T)", "(! (! T))"),
        ("((T))", "T"),
        ("T | T", "(T | T)"),
        ("T|T",   "(T | T)"),
        ("T| T",  "(T | T)"),
        ("T| T",  "(T | T)"),
        ("T |T",  "(T | T)"),
        ("(T|T)", "(T | T)"),
        ("(T)|T", "(T | T)"),
        ("T | T | T", "((T | T) | T)"),
        ("!T|T",  "((! T) | T)"),
        ("T|!T",  "(T | (! T))"),
        ("!(T|T)", "(! (T | T))"),
        ("T & T | T", "((T & T) | T)"),
        ("T | T & T", "(T | (T & T))"),
        ("T->T",   "(T -> T)"),
        ("T<->T",   "(T <-> T)"),
        ("T | T -> T", "((T | T) -> T)"),
        ("T -> T | T", "(T -> (T | T))"),
        ("T -> T -> T", "((T -> T) -> T)"),
        ("T -> T <-> T", "((T -> T) <-> T)"),
        ("T <-> T -> T", "(T <-> (T -> T))"),
        ("A x T",   "(A x T)"),
        ("E x T",   "(E x T)"),
        ("A x A x T",   "(A x (A x T))"),
        ("A x E x T",   "(A x (E x T))"),
        ("E x A x T",   "(E x (A x T))"),
        ("A x T & T",   "((A x T) & T)"),
        ("T & A x T",   "(T & (A x T))"),
        ("! A x T",   "(! (A x T))"),
        ("! E x T",   "(! (E x T))"),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, expected in tests:
        res = Fo.read(test_str)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

def test_read_reorder():
    tests = [
        ("T",   "T"),
        (" T",  "T"),
        ("T ",  "T"),
        ("!T",  "(! T)"),
        ("! T", "(! T)"),
        ("F",   "F"),
        (" F",  "F"),
        ("F ",  "F"),
        ("!F",  "(! F)"),
        ("! F", "(! F)"),
        ("x = x", "x = x"),
        ("y = x", "x = y"),
        ("x12 = x2",  "x12 = x2"),
        ("x12 = x02", "x02 = x12"),
        ("x = y", "x = y"),
        ("x=y",   "x = y"),
        ("(x=y)", "x = y"),
        ("!x=y",  "(! x = y)"),
        ("! x=y", "(! x = y)"),
        ("edg(x,x)",   "edg(x, x)"),
        ("(edg(x,x))", "edg(x, x)"),
        ("edg(y,x)",   "edg(x, y)"),
        ("edg(x,y)",   "edg(x, y)"),
        ("edg(x, y)",  "edg(x, y)"),
        ("edg (x, y)", "edg(x, y)"),
        ("edg(x,y )",  "edg(x, y)"),
        ("edg( x,y)",  "edg(x, y)"),
        ("!edg(x,y)",  "(! edg(x, y))"),
        ("! edg(x,y)", "(! edg(x, y))"),
        ("!!T",   "(! (! T))"),
        ("!(!T)", "(! (! T))"),
        ("((T))", "T"),
        ("T | T", "(T | T)"),
        ("T|T",   "(T | T)"),
        ("T| T",  "(T | T)"),
        ("T| T",  "(T | T)"),
        ("T |T",  "(T | T)"),
        ("(T|T)", "(T | T)"),
        ("(T)|T", "(T | T)"),
        ("T & T & T", "(T & (T & T))"),
        ("T & T & T & T", "((T & T) & (T & T))"),
        ("T & T & T & T & T", "((T & T) & (T & (T & T)))"),
        ("T | T | T", "(T | (T | T))"),
        ("T | T | T | T", "((T | T) | (T | T))"),
        ("T | T | T | T | T", "((T | T) | (T | (T | T)))"),
        ("!T|T",  "((! T) | T)"),
        ("T|!T",  "(T | (! T))"),
        ("!(T|T)", "(! (T | T))"),
        ("T & T | T", "((T & T) | T)"),
        ("T & T | T | T", "((T & T) | (T | T))"),
        ("T | T & T | T", "(T | ((T & T) | T))"),
        ("T | T & T", "(T | (T & T))"),
        ("T & T & T | T", "((T & (T & T)) | T)"),
        ("T->T",   "(T -> T)"),
        ("T<->T",   "(T <-> T)"),
        ("T | T -> T", "((T | T) -> T)"),
        ("T -> T | T", "(T -> (T | T))"),
        ("T -> T -> T", "((T -> T) -> T)"),
        ("T -> T <-> T", "((T -> T) <-> T)"),
        ("T <-> T -> T", "(T <-> (T -> T))"),
        ("A x T",   "(A x T)"),
        ("E x T",   "(E x T)"),
        ("A x A x T",   "(A x (A x T))"),
        ("A x E x T",   "(A x (E x T))"),
        ("E x A x T",   "(E x (A x T))"),
        ("A x T & T",   "((A x T) & T)"),
        ("T & A x T",   "(T & (A x T))"),
        ("! A x T",   "(! (A x T))"),
        ("! E x T",   "(! (E x T))"),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, expected in tests:
        res = Fo.read(test_str, reorder=True)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

def gen_form_rand(depth: int = 3) -> Fo:
    if depth < 1:
        raise ValueError("depth >= 1")

    def gen_atom_rand() -> Fo:
        var_name = ["x","y","z"]
        op1 = NameMgr.lookup_index(random.choice(var_name))
        op2 = NameMgr.lookup_index(random.choice(var_name))

        atom_name = ["edg", "eq", "T", "F"]
        name = random.choice(atom_name)
        if name == "edg":
            return Fo.edg(op1, op2)
        if name == "eq":
            return Fo.eq(op1, op2)
        if name == "T":
            return Fo.true_const()
        if name == "F":
            return Fo.false_const()
        assert False

    op_tag = [\
        Fo.get_forall_tag(), \
        Fo.get_exists_tag(), \
        Fo.get_neg_tag(), \
        Fo.get_land_tag(), \
        Fo.get_lor_tag(), \
        Fo.get_implies_tag(), \
        Fo.get_iff_tag(), \
        "NA",\
    ]
    tag = random.choice(op_tag)

    if depth == 1 or tag == "NA":
        return gen_atom_rand()

    if tag == Fo.get_forall_tag() or tag == Fo.get_exists_tag():
        var_name = ["x","y","z"]
        bvar = NameMgr.lookup_index(random.choice(var_name))
        left = gen_form_rand(depth-1)
        return Fo.qf(tag, left, bvar)

    if tag == Fo.get_neg_tag():
        left = gen_form_rand(depth-1)
        return Fo.neg(left)

    if tag == Fo.get_land_tag() \
        or tag == Fo.get_lor_tag() \
        or tag == Fo.get_implies_tag() \
        or tag == Fo.get_iff_tag():

        left  = gen_form_rand(depth-1)
        right = gen_form_rand(depth-1)
        return Fo.binop(tag, left, right)
    assert False

def test_format():
    NameMgr.clear()
    Fo.st = None

    for x in range(3):
        test_form = gen_form_rand()
        form_str = op.to_str(test_form)
        res_form = Fo.read(form_str)
        assert test_form == res_form


def test_generator():
    tests = [
        ("T",
            ("T"),
            (),
            ("T"),
        ),
        ("T | T",
            ("(T | T)",
            "T",
            "T",),
            ("(T | T)",),
            ("T",
            "T",
            "(T | T)",),
        ),
        ("((!x=y) | edg(x,y)) & (A x (!x=y))",
            ("(((! x = y) | edg(x, y)) & (A x (! x = y)))",
            "((! x = y) | edg(x, y))",
            "(! x = y)",
            "x = y",
            "edg(x, y)",
            "(A x (! x = y))",
            "(! x = y)",
            "x = y",),
            ("((! x = y) | edg(x, y))",
            "(((! x = y) | edg(x, y)) & (A x (! x = y)))",),
            ("x = y",
            "(! x = y)",
            "edg(x, y)",
            "((! x = y) | edg(x, y))",
            "x = y",
            "(! x = y)",
            "(A x (! x = y))",
            "(((! x = y) | edg(x, y)) & (A x (! x = y)))",),
        ),
        ("((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            ("((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            "(x = y & edg(x, y))",
            "x = y",
            "edg(x, y)",
            "(x = y & edg(x, y))",
            "x = y",
            "edg(x, y)",),
            ("(x = y & edg(x, y))",
            "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            "(x = y & edg(x, y))",),
            ("x = y",
            "edg(x, y)",
            "(x = y & edg(x, y))",
            "x = y",
            "edg(x, y)",
            "(x = y & edg(x, y))",
            "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",),
        ),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, prefix_expected, infix_expected, postfix_expected in tests:
        res = Fo.read(test_str)
        pos0 = 0
        pos1 = 0
        pos2 = 0
        for i,g in op.generator(res):
            if i == 0:
                assert pos0 < len(prefix_expected)
                assert op.to_str(g) == prefix_expected[pos0]
                pos0 += 1
                continue
            if i == 1:
                assert pos1 < len(infix_expected)
                assert op.to_str(g) == infix_expected[pos1]
                pos1 += 1
                continue
            if i == 2:
                assert pos2 < len(postfix_expected)
                assert op.to_str(g) == postfix_expected[pos2]
                pos2 += 1
                continue

    tests_skip_shared = [
        ("T | T",
            ("(T | T)",
            "T",),
            ("(T | T)",),
            ("T",
            "(T | T)",),
        ),
        ("((!x=y) | edg(x,y)) & (A x (!x=y))",
            ("(((! x = y) | edg(x, y)) & (A x (! x = y)))",
            "((! x = y) | edg(x, y))",
            "(! x = y)",
            "x = y",
            "edg(x, y)",
            "(A x (! x = y))",),
            ("((! x = y) | edg(x, y))",
            "(((! x = y) | edg(x, y)) & (A x (! x = y)))",),
            ("x = y",
            "(! x = y)",
            "edg(x, y)",
            "((! x = y) | edg(x, y))",
            "(A x (! x = y))",
            "(((! x = y) | edg(x, y)) & (A x (! x = y)))",),
        ),
        ("((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            ("((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            "(x = y & edg(x, y))",
            "x = y",
            "edg(x, y)",),
            ("(x = y & edg(x, y))",
            "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            "(x = y & edg(x, y))",),
            ("x = y",
            "edg(x, y)",
            "(x = y & edg(x, y))",
            "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",),
        ),
    ]

    for test_str, prefix_expected, infix_expected, postfix_expected in tests_skip_shared:
        res = Fo.read(test_str)
        pos0 = 0
        pos1 = 0
        pos2 = 0
        for i,g in op.generator(res, skip_shared=True):
            if i == 0:
                assert pos0 < len(prefix_expected)
                assert op.to_str(g) == prefix_expected[pos0]
                pos0 += 1
                continue
            if i == 1:
                assert pos1 < len(infix_expected)
                assert op.to_str(g) == infix_expected[pos1]
                pos1 += 1
                continue
            if i == 2:
                assert pos2 < len(postfix_expected)
                assert op.to_str(g) == postfix_expected[pos2]
                pos2 += 1
                continue


def test_compute_nnf():
    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = x", "x = x"),
        ("edg(x, x)", "edg(x, x)"),
        ("!T", "(! T)"),
        ("!!T", "T"),
        ("!!!T", "(! T)"),
        ("T  -> F", "((! T) | F)"),
        ("T <-> F", "(((! T) | F) & ((! F) | T))"),
        ("! (T & F)", "((! T) | (! F))"),
        ("! (T | F)", "((! T) & (! F))"),
        ("! (T -> F)", "(T & (! F))"),
        ("! (T <-> F)", "((T & (! F)) | (F & (! T)))"),
        ("! A x T", "(E x (! T))"),
        ("! E x T", "(A x (! T))"),
        ("! A x (T & F)", "(E x ((! T) | (! F)))"),
    ]

    NameMgr.clear()
    Fo.st = None
        
    for test_str, expected in tests:
        res = Fo.read(test_str)
        res = op.compute_nnf(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

def test_reduce():
    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = y", "x = y"),
        ("x = x", "T"),
        ("! T", "F"),
        ("! F", "T"),
        ("edg(x, y)", "edg(x, y)"),
        ("edg(x, x)", "F"),
        ("x = y & T", "x = y"),
        ("x = y & F", "F"),
        ("x = y | T", "T"),
        ("x = y | F", "x = y"),
        ("A x T", "T"),
        ("A x F", "(A x F)"),
        ("E x T", "(E x T)"),
        ("E x F", "F"),
        ("A x (x = x & x = y)", "(A x x = y)"),
        ("! A x (((x = x) | F) & edg(x, y))", "(E x (! edg(x, y)))"),
        ("(E x edg(x, x)) & (E x edg(x, x))", "F"),
        ("(E x edg(x, x)) | (E x edg(x, x))", "F"),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, expected in tests:
        res = Fo.read(test_str)
        res = op.reduce(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"


def test_reduce_with_st():
    tests = [
        ("A x T", "T"),
        ("A x F", "F"),
        ("E x T", "T"),
        ("E x F", "F"),
        ("edg(V1,V2)", "T"),
        ("edg(V1,V3)", "T"),
        ("edg(V2,V3)", "T"),
        ("edg(V3,V4)", "T"),
        ("edg(V3,V5)", "T"),
        ("edg(V4,V5)", "T"),
        ("edg(V1,V4)", "F"),
        ("edg(V1,V5)", "F"),
        ("edg(V2,V4)", "F"),
        ("edg(V2,V5)", "F"),
        ("V1 = V2", "F"),
        ("V1 = V3", "F"),
        ("V1 = V4", "F"),
        ("V1 = V5", "F"),
        ("V2 = V3", "F"),
        ("V2 = V4", "F"),
        ("V2 = V5", "F"),
        ("V3 = V4", "F"),
        ("V3 = V5", "F"),
        ("V4 = V5", "F"),
        ("edg(x, V1)", "edg(V1, x)"),
        ("x = V1", "V1 = x"),
        ("! A x (((x = x) | F) & edg(V1, V3))", "F"),
        ("! E x (((x = x) | F) & edg(V1, V3))", "F"),
    ]

    #
    # V1 --- V2
    #  \    /
    #   \  /
    #    V3
    #   / \
    #  /   \
    # V4---V5
    # Graph G
    #
    # q1 = {V1,V2,V3}
    # q2 = {V3,V4,V5}
    # e2 = {V1,V3}
    # e5 = {V3,V5}
    #
    #    q1  q2 e2 e5
    # V1  1  0  1  0
    # V2  1  0  0  0
    # V3  1  1  1  1
    # V4  0  1  0  0
    # V5  0  1  0  1
    # Vertex-Clique Incidence Matrix of G
    #

    NameMgr.clear()
    Fo.st = None

    dom = ((1,3), (1,), (1,2,3,4), (2,), (2,4))
    st = GrSt(dom)
    Fo.st = st

    for test_str, expected in tests:
        res = Fo.read(test_str)
        res = op.reduce(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    Fo.st = None

def test_get_free_vars_and_consts():
    tests = [
        ("T", ""),
        ("x = y", "x,y"),
        ("x = x", "x"),
        ("edg(x, y)", "x,y"),
        ("edg(x, x)", "x"),
        ("edg(V1, x)", "V1,x"),
        ("A x T", ""),
        ("A x edg(x, x)", ""),
        ("A x edg(z, y)", "y,z"),
        ("A x edg(x, y)", "y"),
        ("E x edg(x, y)", "y"),
        ("A x edg(x, V1)", "V1"),
        ("E x edg(x, V1)", "V1"),
        ("A x A x (x = y)", "y"),
        ("(E x x = y) & (A y y = y)", "y"),
        ("(E x x = y) & (A y x = y)", "x,y"),
        (" x = y & (! edg(x, y)) | x = z", "x,y,z"),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, expected in tests:
        res = Fo.read(test_str)
        tup = op.get_free_vars_and_consts(res)
        name = [NameMgr.lookup_name(i) for i in tup]
        name = sorted(name)
        res_str=",".join(name)
        assert res_str == expected, f"{res_str}, {expected}"

def test_get_free_vars():
    tests = [
        ("edg(V1, x)", "x"),
        ("A x edg(x, V1)", ""),
        ("E x edg(x, V1)", ""),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, expected in tests:
        res = Fo.read(test_str)
        tup = op.get_free_vars(res)
        name = [NameMgr.lookup_name(i) for i in tup]
        name = sorted(name)
        res_str=",".join(name)
        assert res_str == expected, f"{res_str}, {expected}"

def test_eliminate_qf():
    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = y", "x = y"),
        ("edg(x, y)", "edg(x, y)"),
        ("T & T", "(T & T)"),
        ("T | T", "(T | T)"),
        ("T -> T", "(T -> T)"),
        ("T <-> T", "(T <-> T)"),
        ("A x T", "((((T & T) & T) & T) & T)"),
        ("A x x = y", "((((V1 = y & V2 = y) & V3 = y) & V4 = y) & V5 = y)"),
        ("E x T", "((((T | T) | T) | T) | T)"),
        ("E x x = y", "((((V1 = y | V2 = y) | V3 = y) | V4 = y) | V5 = y)"),
        ("T & (E x T)", "(T & ((((T | T) | T) | T) | T))"),
    ]

    #
    # V1 --- V2
    #  \    /
    #   \  /
    #    V3
    #   / \
    #  /   \
    # V4---V5
    # Graph G
    #
    # q1 = {V1,V2,V3}
    # q2 = {V3,V4,V5}
    # e2 = {V1,V3}
    # e5 = {V3,V5}
    #
    #    q1  q2 e2 e5
    # V1  1  0  1  0
    # V2  1  0  0  0
    # V3  1  1  1  1
    # V4  0  1  0  0
    # V5  0  1  0  1
    # Vertex-Clique Incidence Matrix of G
    #

    NameMgr.clear()
    Fo.st = None

    dom = ((1,3), (1,), (1,2,3,4), (2,), (2,4))
    st = GrSt(dom)
    Fo.st = st

    for test_str, expected in tests:
        res = Fo.read(test_str)
        res = op.eliminate_qf(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = y", "x = y"),
        ("edg(x, y)", "edg(x, y)"),
        ("T & T", "T"),
        ("T | T", "T"),
        ("T -> T", "T"),
        ("T <-> T", "T"),
        ("A x T", "T"),
        ("E x T", "T"),
        ("T & (E x T)", "T"),
        ("A x E y edg(x, y)", "T"),
        ("A x E y x = y", "T"),
        ("A x E y (! x = y)", "T"),
        ("E x A y edg(x, y)", "F"),
        ("E x A y (x = y | edg(x, y))", "T"),
    ]


    for test_str, expected in tests:
        res = Fo.read(test_str)
        res = op.eliminate_qf(res)
        res = op.reduce(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    Fo.st = None

def test_substitute():
    tests = [
        ("x = y", "y", "x", "y = y"),
        ("x = y", "V1", "x", "V1 = y"),
        ("x = y", "y", "z", "x = y"),
        ("T", "y", "z", "T"),
        ("edg(x, V1)", "y", "V1", "edg(x, y)"),
        ("edg(x, V1)", "y", "x", "edg(V1, y)"),
        ("A x edg(x, V1)", "y", "x", "(A x edg(V1, x))"),
        ("A x A x edg(x, V1)", "y", "x", "(A x (A x edg(V1, x)))"),
        ("A x E x A x edg(x, V1)", "y", "x", "(A x (E x (A x edg(V1, x))))"),
        ("A x A y edg(x, y)", "y", "x", "(A x (A y edg(x, y)))"),
        ("x = y & A x edg(x, V1)", "y", "x", "(y = y & (A x edg(V1, x)))"),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, op1_str, op2_str, expected in tests:
        form = Fo.read(test_str)
        op1  = NameMgr.lookup_index(op1_str)
        op2  = NameMgr.lookup_index(op2_str)
        res = op.substitute(form, op1, op2)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

def test_propnize():
    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = x", "T"),
        ("edg(x, x)", "F"),
        ("x = y", "((x@1 <-> y@1) & (x@2 <-> y@2))"),
        ("edg(x, y)", "(((x@1 & y@1) | (x@2 & y@2)) & ((! (x@1 <-> y@1)) | (! (x@2 <-> y@2))))"),
        ("x = y | edg(x, y)", "(((x@1 <-> y@1) & (x@2 <-> y@2)) | (((x@1 & y@1) | (x@2 & y@2)) & ((! (x@1 <-> y@1)) | (! (x@2 <-> y@2)))))"),
        ("A x x = y", "(((T <-> y@1) & (T <-> y@2)) & ((T <-> y@1) & (F <-> y@2)))"),
        ("E x x = y", "(((T <-> y@1) & (T <-> y@2)) | ((T <-> y@1) & (F <-> y@2)))"),
    ]

    NameMgr.clear()
    Fo.st = None

    dom = ((1,2), (1,))
    st = GrSt(dom)
    Fo.st = st
    Prop.st = st

    for test_str, expected in tests:
        res = Fo.read(test_str)
        res = op.propnize(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    Fo.st = None
    Prop.st = None

def test_propnize_reorder():
    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = x", "T"),
        ("edg(x, x)", "F"),
        ("x = y", "((x@1 <-> y@1) & ((x@2 <-> y@2) & (x@3 <-> y@3)))"),
        ("edg(x, y)", "(((x@1 & y@1) | ((x@2 & y@2) | (x@3 & y@3))) & ((! (x@1 <-> y@1)) | ((! (x@2 <-> y@2)) | (! (x@3 <-> y@3)))))"),
        ("x = y | edg(x, y)", "(((x@1 <-> y@1) & ((x@2 <-> y@2) & (x@3 <-> y@3))) | (((x@1 & y@1) | ((x@2 & y@2) | (x@3 & y@3))) & ((! (x@1 <-> y@1)) | ((! (x@2 <-> y@2)) | (! (x@3 <-> y@3))))))"),
        ("A x x = y", "(((T <-> y@1) & ((T <-> y@2) & (F <-> y@3))) & (((T <-> y@1) & ((F <-> y@2) & (F <-> y@3))) & ((F <-> y@1) & ((F <-> y@2) & (T <-> y@3)))))"),
        ("E x x = y", "(((T <-> y@1) & ((T <-> y@2) & (F <-> y@3))) | (((T <-> y@1) & ((F <-> y@2) & (F <-> y@3))) | ((F <-> y@1) & ((F <-> y@2) & (T <-> y@3)))))"),
    ]

    NameMgr.clear()
    Fo.st = None

    dom = ((1,2), (1,), (3,))
    st = GrSt(dom)
    Fo.st = st
    Prop.st = st

    for test_str, expected in tests:
        res = Fo.read(test_str)
        res = op.propnize(res, reorder=True)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    Fo.st = None
    Prop.st = None

def test_compute_domain_constraint():
    tests = [
        ("T", ((), (1,)), set()),
        ("A x E y x=y", ((), (1,)), set()),
        ("x=y", ((1,2), (1,)), 
            {"((x@1 & x@2) | (x@1 & (! x@2)))", 
            "((y@1 & y@2) | (y@1 & (! y@2)))"}),
        ("x=y", ((2,), (1,)), 
            {"(((! x@1) & x@2) | (x@1 & (! x@2)))", 
            "(((! y@1) & y@2) | (y@1 & (! y@2)))"}),
        ("x=y", ((), (1,)), 
            {"((! x@1) | x@1)", 
            "((! y@1) | y@1)"}),
    ]

    NameMgr.clear()
    Fo.st = None

    for test_str, test_dom, expected in tests:
        res = Fo.read(test_str)
        st = GrSt(test_dom)
        Fo.st = st
        Prop.st = st

        tup = op.compute_domain_constraint(res)
        res_set = set()
        for i in range(len(tup)):
            res_str = op.to_str(tup[i])
            res_set.add(res_str)
        assert res_set == expected, f"{res_set}, {expected}"

        Fo.st = None
        Prop.st = None

