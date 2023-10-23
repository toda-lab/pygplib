import pytest

from pygplib import NameMgr


def test_lookup_index():
    tests = [
        "",  # Leading character must be alphabetic.
        "@",
        "+",
        "=",
        "_",
        "*",
        "&",
        "|",
        "-",
        ">",
        "<",
    ]

    NameMgr.clear()

    for test_str in tests:
        with pytest.raises(ValueError):
            NameMgr.lookup_index(test_str)


def test_lookup_name():
    NameMgr.clear()
    index = len(NameMgr._inv_list)
    with pytest.raises(IndexError):
        NameMgr.lookup_name(index)
    with pytest.raises(IndexError):
        NameMgr.lookup_name(index + 1)
    with pytest.raises(IndexError):
        NameMgr.lookup_name(-1)
    with pytest.raises(IndexError):
        NameMgr.lookup_name(0)
