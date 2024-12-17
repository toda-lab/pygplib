import pytest
import pyparsing as pp
import pygplib.op as op

from pygplib import Prop, NameMgr, GrSt, Fog


def test_read():
    tests = [
        "{x1}",  # Use "(" and ")" in stead of "{" and "}".
        "[x1]",  #
        "1x1",  # Leading character of symbol name must not be a digit.
        "X_1",  # Use lowercase letters.
        "x_X_1",  #
    ]

    NameMgr.clear()
    for test_str in tests:
        with pytest.raises(pp.ParseException):
            Prop.read(test_str)


def test_format():
    pass


def test_compute_cnf():
    tests = [
        0,
        1,
        "x_1",
        (Fog.read("T"),),
        (
            Prop.read("T"),
            Fog.read("T"),
        ),
    ]

    NameMgr.clear()

    for test_arg in tests:
        with pytest.raises(TypeError):
            op.compute_cnf(test_arg)
