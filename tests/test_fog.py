import random

from pygplib import Fog, NameMgr, GrSt, Prop
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
        ("x = x", "x = x"),
        ("y = x", "x = y"),
        ("x12 = x2", "x12 = x2"),
        ("x12 = x02", "x02 = x12"),
        ("x = y", "x = y"),
        ("x=y", "x = y"),
        ("(x=y)", "x = y"),
        ("~x=y", "(~ x = y)"),
        ("~ x=y", "(~ x = y)"),
        ("edg(x,x)", "edg(x, x)"),
        ("(edg(x,x))", "edg(x, x)"),
        ("edg(y,x)", "edg(x, y)"),
        ("edg(x,y)", "edg(x, y)"),
        ("edg(x, y)", "edg(x, y)"),
        ("edg (x, y)", "edg(x, y)"),
        ("edg(x,y )", "edg(x, y)"),
        ("edg( x,y)", "edg(x, y)"),
        ("~edg(x,y)", "(~ edg(x, y))"),
        ("~ edg(x,y)", "(~ edg(x, y))"),
        ("~~T", "(~ (~ T))"),
        ("~(~T)", "(~ (~ T))"),
        ("((T))", "T"),
        ("T | F", "(T | F)"),
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
        ("! [x] : T", "(! [x] : T)"),
        ("? [x] : T", "(? [x] : T)"),
        ("! [x] : ! [x] : T", "(! [x] : (! [x] : T))"),
        ("! [x] : ? [x] : T", "(! [x] : (? [x] : T))"),
        ("? [x] : ! [x] : T", "(? [x] : (! [x] : T))"),
        ("! [x] : T & T", "((! [x] : T) & T)"),
        ("T & ! [x] : T", "(T & (! [x] : T))"),
        ("~ ! [x] : T", "(~ (! [x] : T))"),
        ("~ ? [x] : T", "(~ (? [x] : T))"),
        ("x =x", "x = x"),
        ("x= x", "x = x"),
        ("x=x", "x = x"),
        ("x12x = X12X", "X12X = x12x"),
        ("x1x4 = X12X4", "X12X4 = x1x4"),
        ("x_x = X_X", "X_X = x_x"),
        ("![x]:(T|F)", "(! [x] : (T | F))"),
        ("![x]:(T& F|T)", "(! [x] : ((T & F) | T))"),
        ("?[x]:(T& F|T)", "(? [x] : ((T & F) | T))"),
        ("?[x]:(~T)", "(? [x] : (~ T))"),
        ("x=x & ~x=x", "(x = x & (~ x = x))"),
        ("~x=x & x=x", "((~ x = x) & x = x)"),
        ("![x]: T", "(! [x] : T)"),
        ("![x]:T", "(! [x] : T)"),
        ("![ x]:T", "(! [x] : T)"),
        ("![x ]:T", "(! [x] : T)"),
        ("! [x]:T", "(! [x] : T)"),
        ("?[x]: T", "(? [x] : T)"),
        ("?[x]:T", "(? [x] : T)"),
        ("?[ x]:T", "(? [x] : T)"),
        ("?[x ]:T", "(? [x] : T)"),
        ("? [x]:T", "(? [x] : T)"),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, expected in tests:
        res = Fog.read(test_str)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"


def test_read_bipartite_order():
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
        ("x = x", "x = x"),
        ("y = x", "x = y"),
        ("x12 = x2", "x12 = x2"),
        ("x12 = x02", "x02 = x12"),
        ("x = y", "x = y"),
        ("x=y", "x = y"),
        ("(x=y)", "x = y"),
        ("~x=y", "(~ x = y)"),
        ("~ x=y", "(~ x = y)"),
        ("edg(x,x)", "edg(x, x)"),
        ("(edg(x,x))", "edg(x, x)"),
        ("edg(y,x)", "edg(x, y)"),
        ("edg(x,y)", "edg(x, y)"),
        ("edg(x, y)", "edg(x, y)"),
        ("edg (x, y)", "edg(x, y)"),
        ("edg(x,y )", "edg(x, y)"),
        ("edg( x,y)", "edg(x, y)"),
        ("~edg(x,y)", "(~ edg(x, y))"),
        ("~ edg(x,y)", "(~ edg(x, y))"),
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
        ("T & T & T", "(T & (T & T))"),
        ("T & T & T & T", "((T & T) & (T & T))"),
        ("T & T & T & T & T", "((T & T) & (T & (T & T)))"),
        ("T | T | T", "(T | (T | T))"),
        ("T | T | T | T", "((T | T) | (T | T))"),
        ("T | T | T | T | T", "((T | T) | (T | (T | T)))"),
        ("~T|T", "((~ T) | T)"),
        ("T|~T", "(T | (~ T))"),
        ("~(T|T)", "(~ (T | T))"),
        ("T & T | T", "((T & T) | T)"),
        ("T & T | T | T", "((T & T) | (T | T))"),
        ("T | T & T | T", "(T | ((T & T) | T))"),
        ("T | T & T", "(T | (T & T))"),
        ("T & T & T | T", "((T & (T & T)) | T)"),
        ("T->T", "(T -> T)"),
        ("T<->T", "(T <-> T)"),
        ("T | T -> T", "((T | T) -> T)"),
        ("T -> T | T", "(T -> (T | T))"),
        ("T -> T -> T", "((T -> T) -> T)"),
        ("T -> T <-> T", "((T -> T) <-> T)"),
        ("T <-> T -> T", "(T <-> (T -> T))"),
        ("! [x] : T", "(! [x] : T)"),
        ("? [x] : T", "(? [x] : T)"),
        ("! [x] : ! [x] : T", "(! [x] : (! [x] : T))"),
        ("! [x] : ? [x] : T", "(! [x] : (? [x] : T))"),
        ("? [x] : ! [x] : T", "(? [x] : (! [x] : T))"),
        ("! [x] : T & T", "((! [x] : T) & T)"),
        ("T & ! [x] : T", "(T & (! [x] : T))"),
        ("~ ! [x] : T", "(~ (! [x] : T))"),
        ("~ ? [x] : T", "(~ (? [x] : T))"),
    ]

    NameMgr.clear()
    Fog.st = None
    Fog.bipartite_order = True

    for test_str, expected in tests:
        res = Fog.read(test_str)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    Fog.bipartite_order = False


def gen_form_rand(depth: int = 3) -> Fog:
    if depth < 1:
        raise ValueError("depth >= 1")

    def gen_atom_rand() -> Fog:
        var_name = ["x", "y", "z"]
        op1 = NameMgr.lookup_index(random.choice(var_name))
        op2 = NameMgr.lookup_index(random.choice(var_name))

        atom_name = ["edg", "eq", "T", "F"]
        name = random.choice(atom_name)
        if name == "edg":
            return Fog.edg(op1, op2)
        if name == "eq":
            return Fog.eq(op1, op2)
        if name == "T":
            return Fog.true_const()
        if name == "F":
            return Fog.false_const()
        assert False

    op_tag = [
        Fog.get_forall_tag(),
        Fog.get_exists_tag(),
        Fog.get_neg_tag(),
        Fog.get_land_tag(),
        Fog.get_lor_tag(),
        Fog.get_implies_tag(),
        Fog.get_iff_tag(),
        "NA",
    ]
    tag = random.choice(op_tag)

    if depth == 1 or tag == "NA":
        return gen_atom_rand()

    if tag == Fog.get_forall_tag() or tag == Fog.get_exists_tag():
        var_name = ["x", "y", "z"]
        bvar = NameMgr.lookup_index(random.choice(var_name))
        left = gen_form_rand(depth - 1)
        return Fog.qf(tag, left, bvar)

    if tag == Fog.get_neg_tag():
        left = gen_form_rand(depth - 1)
        return Fog.neg(left)

    if (
        tag == Fog.get_land_tag()
        or tag == Fog.get_lor_tag()
        or tag == Fog.get_implies_tag()
        or tag == Fog.get_iff_tag()
    ):

        left = gen_form_rand(depth - 1)
        right = gen_form_rand(depth - 1)
        return Fog.binop(tag, left, right)
    assert False


def test_format():
    NameMgr.clear()
    Fog.st = None

    for x in range(3):
        test_form = gen_form_rand()
        form_str = op.to_str(test_form)
        res_form = Fog.read(form_str)
        assert test_form == res_form


def test_generator():
    tests = [
        (
            "T",
            ("T"),
            (),
            ("T"),
        ),
        (
            "T | T",
            (
                "(T | T)",
                "T",
                "T",
            ),
            ("(T | T)",),
            (
                "T",
                "T",
                "(T | T)",
            ),
        ),
        (
            "((~x=y) | edg(x,y)) & (! [x] : (~x=y))",
            (
                "(((~ x = y) | edg(x, y)) & (! [x] : (~ x = y)))",
                "((~ x = y) | edg(x, y))",
                "(~ x = y)",
                "x = y",
                "edg(x, y)",
                "(! [x] : (~ x = y))",
                "(~ x = y)",
                "x = y",
            ),
            (
                "((~ x = y) | edg(x, y))",
                "(((~ x = y) | edg(x, y)) & (! [x] : (~ x = y)))",
            ),
            (
                "x = y",
                "(~ x = y)",
                "edg(x, y)",
                "((~ x = y) | edg(x, y))",
                "x = y",
                "(~ x = y)",
                "(! [x] : (~ x = y))",
                "(((~ x = y) | edg(x, y)) & (! [x] : (~ x = y)))",
            ),
        ),
        (
            "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            (
                "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
                "(x = y & edg(x, y))",
                "x = y",
                "edg(x, y)",
                "(x = y & edg(x, y))",
                "x = y",
                "edg(x, y)",
            ),
            (
                "(x = y & edg(x, y))",
                "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
                "(x = y & edg(x, y))",
            ),
            (
                "x = y",
                "edg(x, y)",
                "(x = y & edg(x, y))",
                "x = y",
                "edg(x, y)",
                "(x = y & edg(x, y))",
                "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            ),
        ),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, prefix_expected, infix_expected, postfix_expected in tests:
        res = Fog.read(test_str)
        pos0 = 0
        pos1 = 0
        pos2 = 0
        for i, g in op.generator(res):
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
        (
            "T | T",
            (
                "(T | T)",
                "T",
            ),
            ("(T | T)",),
            (
                "T",
                "(T | T)",
            ),
        ),
        (
            "((~x=y) | edg(x,y)) & (! [x] : (~x=y))",
            (
                "(((~ x = y) | edg(x, y)) & (! [x] : (~ x = y)))",
                "((~ x = y) | edg(x, y))",
                "(~ x = y)",
                "x = y",
                "edg(x, y)",
                "(! [x] : (~ x = y))",
            ),
            (
                "((~ x = y) | edg(x, y))",
                "(((~ x = y) | edg(x, y)) & (! [x] : (~ x = y)))",
            ),
            (
                "x = y",
                "(~ x = y)",
                "edg(x, y)",
                "((~ x = y) | edg(x, y))",
                "(! [x] : (~ x = y))",
                "(((~ x = y) | edg(x, y)) & (! [x] : (~ x = y)))",
            ),
        ),
        (
            "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            (
                "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
                "(x = y & edg(x, y))",
                "x = y",
                "edg(x, y)",
            ),
            (
                "(x = y & edg(x, y))",
                "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
                "(x = y & edg(x, y))",
            ),
            (
                "x = y",
                "edg(x, y)",
                "(x = y & edg(x, y))",
                "((x = y & edg(x, y)) -> (x = y & edg(x, y)))",
            ),
        ),
    ]

    for (
        test_str,
        prefix_expected,
        infix_expected,
        postfix_expected,
    ) in tests_skip_shared:
        res = Fog.read(test_str)
        pos0 = 0
        pos1 = 0
        pos2 = 0
        for i, g in op.generator(res, skip_shared=True):
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
        ("~T", "(~ T)"),
        ("~~T", "T"),
        ("~~~T", "(~ T)"),
        ("T  -> F", "((~ T) | F)"),
        ("T <-> F", "(((~ T) | F) & ((~ F) | T))"),
        ("~ (T & F)", "((~ T) | (~ F))"),
        ("~ (T | F)", "((~ T) & (~ F))"),
        ("~ (T -> F)", "(T & (~ F))"),
        ("~ (T <-> F)", "((T & (~ F)) | (F & (~ T)))"),
        ("~ ! [x] : T", "(? [x] : (~ T))"),
        ("~ ? [x] : T", "(! [x] : (~ T))"),
        ("~ ! [x] : (T & F)", "(? [x] : ((~ T) | (~ F)))"),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, expected in tests:
        res = Fog.read(test_str)
        res = op.compute_nnf(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"


def test_reduce():
    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = y", "x = y"),
        ("x = x", "T"),
        ("~ T", "F"),
        ("~ F", "T"),
        ("edg(x, y)", "edg(x, y)"),
        ("edg(x, x)", "F"),
        ("x = y & T", "x = y"),
        ("x = y & F", "F"),
        ("x = y | T", "T"),
        ("x = y | F", "x = y"),
        ("! [x] : T", "T"),
        ("! [x] : F", "(! [x] : F)"),
        ("? [x] : T", "(? [x] : T)"),
        ("? [x] : F", "F"),
        ("! [x] : (x = x & x = y)", "(! [x] : x = y)"),
        ("~ ! [x] : (((x = x) | F) & edg(x, y))", "(? [x] : (~ edg(x, y)))"),
        ("(? [x] : edg(x, x)) & (? [x] : edg(x, x))", "F"),
        ("(? [x] : edg(x, x)) | (? [x] : edg(x, x))", "F"),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, expected in tests:
        res = Fog.read(test_str)
        res = op.reduce(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"


def test_reduce_with_st():
    tests = [
        ("! [x] : T", "T"),
        ("! [x] : F", "F"),
        ("? [x] : T", "T"),
        ("? [x] : F", "F"),
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
        ("~ ! [x] : (((x = x) | F) & edg(V1, V3))", "F"),
        ("~ ? [x] : (((x = x) | F) & edg(V1, V3))", "F"),
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
    Fog.st = None

    vertex_list = [1,2,3,4,5]
    edge_list = [(1,2),(1,3),(2,3),(3,4),(3,5),(4,5)]

    for encoding in ["edge", "clique", "direct"]:
        Fog.st = GrSt(vertex_list, edge_list, encoding=encoding)

        for test_str, expected in tests:
            res = Fog.read(test_str)
            res = op.reduce(res)
            res_str = op.to_str(res)
            assert res_str == expected, f"{res_str}, {expected}"

    Fog.st = None


def test_get_free_vars_and_consts():
    tests = [
        ("T", ""),
        ("x = y", "x,y"),
        ("x = x", "x"),
        ("edg(x, y)", "x,y"),
        ("edg(x, x)", "x"),
        ("edg(V1, x)", "V1,x"),
        ("! [x] : T", ""),
        ("! [x] : edg(x, x)", ""),
        ("! [x] : edg(z, y)", "y,z"),
        ("! [x] : edg(x, y)", "y"),
        ("? [x] : edg(x, y)", "y"),
        ("! [x] : edg(x, V1)", "V1"),
        ("? [x] : edg(x, V1)", "V1"),
        ("! [x] : ! [x] : (x = y)", "y"),
        ("(? [x] : x = y) & (! [y] : y = y)", "y"),
        ("(? [x] : x = y) & (! [y] : x = y)", "x,y"),
        (" x = y & (~ edg(x, y)) | x = z", "x,y,z"),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, expected in tests:
        res = Fog.read(test_str)
        tup = op.get_free_vars_and_consts(res)
        name = [NameMgr.lookup_name(i) for i in tup]
        name = sorted(name)
        res_str = ",".join(name)
        assert res_str == expected, f"{res_str}, {expected}"


def test_get_free_vars():
    tests = [
        ("edg(V1, x)", "x"),
        ("! [x] : edg(x, V1)", ""),
        ("? [x] : edg(x, V1)", ""),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, expected in tests:
        res = Fog.read(test_str)
        tup = op.get_free_vars(res)
        name = [NameMgr.lookup_name(i) for i in tup]
        name = sorted(name)
        res_str = ",".join(name)
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
        ("! [x] : T", "((((T & T) & T) & T) & T)"),
        ("! [x] : x = y", "((((V1 = y & V2 = y) & V3 = y) & V4 = y) & V5 = y)"),
        ("? [x] : T", "((((T | T) | T) | T) | T)"),
        ("? [x] : x = y", "((((V1 = y | V2 = y) | V3 = y) | V4 = y) | V5 = y)"),
        ("T & (? [x] : T)", "(T & ((((T | T) | T) | T) | T))"),
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
    Fog.st = None

    vertex_list = [1,2,3,4,5]
    edge_list = [(1,2),(1,3),(2,3),(3,4),(3,5),(4,5)]

    for encoding in ["edge", "clique", "direct"]:
        Fog.st = GrSt(vertex_list, edge_list, encoding=encoding)
        for test_str, expected in tests:
            res = Fog.read(test_str)
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
        ("! [x] : T", "T"),
        ("? [x] : T", "T"),
        ("T & (? [x] : T)", "T"),
        ("! [x] : ? [y] : edg(x, y)", "T"),
        ("! [x] : ? [y] : x = y", "T"),
        ("! [x] : ? [y] : (~ x = y)", "T"),
        ("? [x] : ! [y] : edg(x, y)", "F"),
        ("? [x] : ! [y] : (x = y | edg(x, y))", "T"),
    ]

    for encoding in ["edge", "clique", "direct"]:
        Fog.st = GrSt(vertex_list, edge_list, encoding=encoding)
        for test_str, expected in tests:
            res = Fog.read(test_str)
            res = op.eliminate_qf(res)
            res = op.reduce(res)
            res_str = op.to_str(res)
            assert res_str == expected, f"{res_str}, {expected}"

    Fog.st = None


def test_substitute():
    tests = [
        ("x = y", "y", "x", "y = y"),
        ("x = y", "V1", "x", "V1 = y"),
        ("x = y", "y", "z", "x = y"),
        ("T", "y", "z", "T"),
        ("edg(x, V1)", "y", "V1", "edg(x, y)"),
        ("edg(x, V1)", "y", "x", "edg(V1, y)"),
        ("! [x] : edg(x, V1)", "y", "x", "(! [x] : edg(V1, x))"),
        ("! [x] : ! [x] : edg(x, V1)", "y", "x", "(! [x] : (! [x] : edg(V1, x)))"),
        ("! [x] : ? [x] : ! [x] : edg(x, V1)", "y", "x", "(! [x] : (? [x] : (! [x] : edg(V1, x))))"),
        ("! [x] : ! [y] : edg(x, y)", "y", "x", "(! [x] : (! [y] : edg(x, y)))"),
        ("x = y & ! [x] : edg(x, V1)", "y", "x", "(y = y & (! [x] : edg(V1, x)))"),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, op1_str, op2_str, expected in tests:
        form = Fog.read(test_str)
        op1 = NameMgr.lookup_index(op1_str)
        op2 = NameMgr.lookup_index(op2_str)
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
        (
            "edg(x, y)",
            "(((x@1 & y@1) | (x@2 & y@2)) & (~ ((x@1 <-> y@1) & (x@2 <-> y@2))))",
        ),
        (
            "x = y | edg(x, y)",
            "(((x@1 <-> y@1) & (x@2 <-> y@2)) | (((x@1 & y@1) | (x@2 & y@2)) & (~ ((x@1 <-> y@1) & (x@2 <-> y@2)))))",
        ),
        ("! [x] : x = y", "((((T <-> y@1) & (F <-> y@2)) & ((T <-> y@1) & (T <-> y@2))) & ((F <-> y@1) & (T <-> y@2)))"),
        ("? [x] : x = y", "((((T <-> y@1) & (F <-> y@2)) | ((T <-> y@1) & (T <-> y@2))) | ((F <-> y@1) & (T <-> y@2)))"),
    ]

    NameMgr.clear()
    #  | 1 2
    #--------
    # 1| 1 0
    # 2| 1 1
    # 3| 0 1
    vertex_list = [1,2,3]
    edge_list= [(1,2), (2,3)]
    st = GrSt(vertex_list, edge_list)
    Fog.st = st
    Prop.st = st

    for test_str, expected in tests:
        res = Fog.read(test_str)
        res = op.propnize(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    Fog.st = None
    Prop.st = None


def test_propnize_bipartite_order():
    tests = [
        ("T", "T"),
        ("F", "F"),
        ("x = x", "T"),
        ("edg(x, x)", "F"),
        ("x = y", "((x@1 <-> y@1) & (x@2 <-> y@2))"),
        (
            "edg(x, y)",
            "(((x@1 & y@1) | (x@2 & y@2)) & (~ ((x@1 <-> y@1) & (x@2 <-> y@2))))",
        ),
        (
            "x = y | edg(x, y)",
            "(((x@1 <-> y@1) & (x@2 <-> y@2)) | (((x@1 & y@1) | (x@2 & y@2)) & (~ ((x@1 <-> y@1) & (x@2 <-> y@2)))))",
        ),
        (
            "! [x] : x = y",
            "(((T <-> y@1) & (F <-> y@2)) & (((T <-> y@1) & (T <-> y@2)) & ((F <-> y@1) & (T <-> y@2))))",
        ),
        (
            "? [x] : x = y",
            "(((T <-> y@1) & (F <-> y@2)) | (((T <-> y@1) & (T <-> y@2)) | ((F <-> y@1) & (T <-> y@2))))",
        ),
    ]

    NameMgr.clear()
    Fog.st = None
    Fog.bipartite_order = True
    Prop.bipartite_order = True
    #  | 1 2
    #--------
    # 1| 1 0
    # 2| 1 1
    # 3| 0 1
    vertex_list = [1,2,3]
    edge_list= [(1,2), (2,3)]
    st = GrSt(vertex_list, edge_list)
    Fog.st = st
    Prop.st = st

    for test_str, expected in tests:
        res = Fog.read(test_str)
        res = op.propnize(res)
        res_str = op.to_str(res)
        assert res_str == expected, f"{res_str}, {expected}"

    Fog.st = None
    Prop.st = None
    Fog.bipartite_order = False
    Prop.bipartite_order = False
