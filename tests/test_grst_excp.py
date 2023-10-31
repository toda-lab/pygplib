from pygplib import GrSt, NameMgr, Fog
import pytest


def test_init():
    tests = [
        (
            # vertex_list
            [2,1],
            # edge_list
            [
                (2,1),
                (2,1), # muptiple edges
            ],
            # encoding
            "edge",
            # prefix
            "V",
            # expected
            Exception,
        ),
        (
            # vertex_list
            [2,3,2,1],   # duplication!
            # edge_list
            [
                (2,1),
                (3,1),
                (2,3),
            ],
            # encoding
            "edge",
            # prefix
            "V",
            # expected
            Exception,
        ),
        (
            # vertex_list
            [2,3,1],
            # edge_list
            [
                (3,1),
                (2,),  # non-edge!
                (2,3),
            ],
            # encoding
            "edge",
            # prefix
            "V",
            # expected
            Exception,
        ),
        (
            # vertex_list
            [2,3,1],
            # edge_list
            [
                (3,1),
                (2,2),  # loop!
                (2,3),
            ],
            # encoding
            "edge",
            # prefix
            "V",
            # expected
            Exception,
        ),
        (
            # vertex_list
            [2,3,1],
            # edge_list
            [
                (3,1),
                (2,4),  # 4 not in vertex_list!
                (2,3),
            ],
            # encoding
            "edge",
            # prefix
            "V",
            # expected
            Exception,
        ),
        (
            # vertex_list
            [2,3,1],
            # edge_list
            [
                (3,1),
                (2,1),
                (2,3),
            ],
            # encoding
            "edge",
            # prefix
            "v", # must be uppercase!
            # expected
            Exception,
        ),
        (
            # vertex_list
            [2,3,1],
            # edge_list
            [
                (3,1),
                (2,1),
                (2,3),
            ],
            # encoding
            "edge",
            # prefix
            "Vertex", # must be uppercase!
            # expected
            Exception,
        ),
        (
            # vertex_list
            [2,3,1],
            # edge_list
            [
                (3,1),
                (2,1),
                (2,3),
            ],
            # encoding
            "edg",  # typo!
            # prefix
            "V",
            # expected
            Exception,
        ),
        (
            #  V1---V2
            #  |   /
            #  |  /
            #  | /
            #  V3---V5
            #
            # vertex_list
            [2,3,1,5],
            # edge_list
            [
                (2,1),
                (3,5), # non-separating!
            ],
            # encoding
            "edge",    # in edge-encoding
            # prefix
            "V",
            # expected
            Exception,
        ),
        (
            #  V1---V2
            #  |   /
            #  |  /
            #  | /
            #  V3---V5
            #
            # vertex_list
            [2,3,1,5],
            # edge_list
            [
                (2,1),
                (3,5), # non-separating!
            ],
            # encoding
            "clique",  # in clique-encoding
            # prefix
            "V",
            # expected
            Exception,
        ),
    ]

    for vertex_list, edge_list, encoding, prefix, expected in tests:
        NameMgr.clear()
        with pytest.raises(expected):
            st = GrSt(vertex_list,edge_list,encoding=encoding,prefix=prefix)
