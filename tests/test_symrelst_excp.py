import pytest
from pygplib import SymRelSt, NameMgr

def test_init():
    tests = [
        #      1 2 3
        #   1: 1 0 1
        #   3: 0 1 1
        #   2: 1 0 1
        (
            (1,3,2),
            ((1,2), (3,),(1,3,2)),
            # duplicate codes
            Exception
        ),
        #      1 2 3
        #   1: 1 0 1
        #   2: 0 1 1
        #   2: 1 0 1
        (
            (1,2,2),
            ((1,2), (2,),(1,2)),
            # duplicate objects
            Exception
        ),
        #      1 2 3
        #   1: 1 0 1
        #   2: 0 1 1
        #   2: 1 0 1
        (
            (1,2,2),
            ((1,2), (2,),(1,2,2)),
            # duplicate objects
            Exception
        ),
        #      1 2 3
        #   1: 1 0 1
        #   2: 0 1 1
        #   2: 1 0 1
        (
            (1,2,2),
            ((1,2), (2,),(0,2,2)),
            # invalid relation instance
            Exception
        ),
    ]


    for domain, relation, expected in tests:
        NameMgr.clear()
        max_obj = 4
        universe = set([NameMgr.lookup_index(f"V{i+1}")\
                         for i in range(max_obj)])
        for obj in domain:
            assert obj in universe, \
                f"test case include object {obj} outside universe."

        with pytest.raises(expected):
            SymRelSt(domain, relation)
