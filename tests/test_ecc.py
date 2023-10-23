from pygplib import Ecc

def test_init():
    tests = [
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
                (3,1),
                (2,3),
                (3,5),
            ],
            # _invdic
            {
                (1,2) : 0,
                (1,3) : 1,
                (2,3) : 2,
                (3,5) : 3,
                2 : 0,
                3 : 1,
                1 : 2,
                5 : 3,
            },
            # N
            {
                1: {2,3},
                2: {1,3},
                3: {1,2,5},
                5: {3},
            }
        ),
    ]

    for vertex_list, edge_list, _invdic, N in tests:
        obj = Ecc(vertex_list, edge_list)
        for key in obj._invdic.keys():
            val = obj._invdic[key]
            assert key in _invdic
            assert _invdic[key] == val
        for key in _invdic.keys():
            val = _invdic[key]
            assert key in obj._invdic
            assert obj._invdic[key] == val
        for key in obj._N.keys():
            val = obj._N[key]
            assert key in N
            assert N[key] == val
        for key in N.keys():
            val = N[key]
            assert key in obj._N
            assert obj._N[key] == val

def test__select_uncovered_edge():
    #  V1---V2
    #  |   /
    #  |  /
    #  | /
    #  V3---V5
    #
    vertex_list = [2,3,1,5]
    edge_list = \
            [
                (2,1),
                (3,1),
                (2,3),
                (3,5),
            ]
    tests = (
        (
            # U:
            [(1,2),(1,3),(2,3)],
            # variant
            "r",
        ),
    )

    obj = Ecc(vertex_list, edge_list)
    for U, variant in tests:
        if variant == "r":
            for i in range(10):
                u,v = obj._select_uncovered_edge(U,variant=variant)
                assert u in obj.verts
                assert v in obj.verts
                e = tuple(sorted([u,v])) 
                assert e in U
        
def test__find_clique_covering():
    #  V1---V2
    #  |   /
    #  |  /
    #  | /
    #  V3---V5
    #
    vertex_list = [2,3,1,5]
    edge_list = \
            [
                (2,1),
                (3,1),
                (2,3),
                (3,5),
            ]
    tests = (
        (
            # u:
            1,
            # v:
            2,
            # U:
            [(1,2),(1,3),(2,3)],
            # variant
            "r",
            # Q
            (1,2,3),
        ),
        (
            # u:
            3,
            # v:
            5,
            # U:
            [(1,2), (1,3), (2,3), (3,5)],
            # variant
            "r",
            # Q
            (3,5),
        ),
    )

    obj = Ecc(vertex_list, edge_list)
    for u, v, U, variant, expected in tests:
        if variant == "r":
            for i in range(10):
                Q = obj._find_clique_covering(u,v,U,variant=variant)
                assert Q == expected

def test__mark_all_edges_covered():
    #  V1---V2
    #  |   /
    #  |  /
    #  | /
    #  V3---V5
    #
    vertex_list = [2,3,1,5]
    edge_list = \
            [
                (2,1),
                (3,1),
                (2,3),
                (3,5),
            ]
    tests = (
        (
            # Q:
            (1,2,3),
            # U:
            [(1,2),(1,3),(2,3)],
            # pi:
            [0,1,2,3],
            # expected
            {
                "U" : [],
            }
        ),
    )

    obj = Ecc(vertex_list, edge_list)
    for Q,U,pi,expected in tests:
        obj._mark_all_edges_covered(Q,U,pi)
        assert U == expected["U"]
        assert set(pi) == set([i for i in range(len(obj.edges))])

def test_compute_ecc():
    tests = (
        (
            #  V1---V2
            #  |   /|
            #  |  / |
            #  | /  |
            #  V3---V5
            #
            # vertex_list
            [2,3,1,5],
            # edge_list
            [
                (2,1),
                (3,1),
                (2,3),
                (3,5),
                (2,5),
            ],
            # variant
            "rr",
        ),
    )

    for vertex_list, edge_list, variant in tests:
        obj = Ecc(vertex_list, edge_list)
        res = obj.compute_ecc(variant=variant)

        # clique?
        for Q in res:
            for u in Q:
                for v in Q:
                    if u != v:
                        e = tuple(sorted([u,v]))
                        assert e in obj.edges

        # edge cover?
        for edge in obj.edges:
            found = False
            for Q in res:
                if edge[0] in Q and edge[1] in Q:
                    found = True
                    break
            assert found

def test_compute_separating_ecc():
    tests = (
        (
            #  V1---V2
            #  |   /|
            #  |  / |
            #  | /  |
            #  V3---V5
            #
            # vertex_list
            [2,3,1,5],
            # edge_list
            [
                (2,1),
                (3,1),
                (2,3),
                (3,5),
                (2,5),
            ],
            # variant
            "rr",
        ),
    )

    for vertex_list, edge_list, variant in tests:
        obj = Ecc(vertex_list, edge_list)
        res = obj.compute_separating_ecc(variant=variant)

        # clique?
        for Q in res:
            for u in Q:
                for v in Q:
                    if u != v:
                        e = tuple(sorted([u,v]))
                        assert e in obj.edges

        # edge cover?
        for edge in obj.edges:
            found = False
            for Q in res:
                if edge[0] in Q and edge[1] in Q:
                    found = True
                    break
            assert found

