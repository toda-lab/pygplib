import pytest
import pyparsing as pp
import pygplib.op as op

from pygplib import Prop, NameMgr, GrSt, Fog


def test_read():
    tests = [
        "{x@1}",  # Use "(" and ")" in stead of "{" and "}".
        "[x@1]",  #
        "1x@1",  # Leading character of symbol name must not be a digit.
        "_x@1",  # Leading character of symbol name must not be a symbol.
        "@1",  # Leading character of symbol name must not be a symbol.
        "x",  # Variable must include "@".
        "x@",  # Variable must include at least one digit after "@".
        "x@@1",  # Variable must include exactly one "@".
        "x@_1",  # Variable must not include non-digit characters after "@".
        "X@1",  # Use lowercase letters.
        "x_X@1",  #
    ]

    NameMgr.clear()
    for test_str in tests:
        with pytest.raises(pp.ParseException):
            Prop.read(test_str)


def test_format():
    pass


def test_compute_cnf():
    tests = [
        0,  # Tuple of Propes must be given as input argument.
        1,
        "x@1",
        Prop.read("T"),
        [Prop.read("T")],
        {Prop.read("T")},
        (),  # Tuple must be non-empty
        (Fog.read("T"),),  # Expression must be an instance of Prop or its subclass
        (
            Prop.read("T"),
            Fog.read("T"),
        ),
    ]

    NameMgr.clear()

    for test_arg in tests:
        with pytest.raises(TypeError):
            op.compute_cnf(test_arg)
