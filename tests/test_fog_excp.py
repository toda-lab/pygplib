import pytest
import pyparsing as pp

from pygplib import Fog, NameMgr, GrSt, Prop
import pygplib.op as op


def test_read():
    tests = [
        "x != y",  # Write ! x = y .
        "{x = y}",  # Use "(" and ")" in stead of "{" and "}".
        "[x = y]",  #
        "_x = y",  # Leading character of symbol name must not be a symbol.
        "1x = y",  # Leading character of symbol name must not be a digit.
        "xX = y",  # Do not mix lowercase and uppercase letters.
        "Vv = y",  #
        "x@ = y",  # First-order variable must not include "@".
        "! [x] : ~ T",  # Write ! [x] : (~ T) because it is interpreted as (! [x] : ~) T due to precedence.
        "! [V] : T",  # Bound variable must not be a constant symbol.
    ]

    NameMgr.clear()
    for test_str in tests:
        with pytest.raises(pp.ParseException):
            Fog.read(test_str)


def test_format():
    pass


def test_generator():
    pass


def test_compute_nnf():
    pass


def test_reduce():
    pass


def test_reduce_with_st():
    pass


def test_get_free_vars_and_consts():
    pass


def test_get_free_vars():
    pass


def test_eliminate_qf():
    NameMgr.clear()
    Fog.st = None

    form = Fog.read("T")
    with pytest.raises(Exception):
        op.eliminate_qf(form)

    #  | 1 2
    #--------
    # 1| 1 0
    # 2| 1 1
    # 3| 0 1
    vertex_list = [1,2,3]
    edge_list= [(1,2), (2,3)]
    Fog.st = GrSt(vertex_list, edge_list)

    res = op.eliminate_qf(form)
    res_str = op.to_str(res)
    assert res_str == "T"

    Fog.st = None


def test_substitute():
    NameMgr.clear()

    form = Fog.read("x = y")

    with pytest.raises(ValueError):
        op.substitute(form, 0, 0)

    x = len(NameMgr._inv_list) + 1
    with pytest.raises(ValueError):
        op.substitute(form, x, x)


def test_propnize():
    pass
