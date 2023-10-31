from pygplib import GrSt, NameMgr, Fog, Prop
from pygplib import op


def test_init():
    # tests for exceptional graphs
    tests = [
        (
            # vertex_list
            [],  # empty graph!
            # edge_list
            [],
            # encoding
            "edge",  # in edge-encoding
        ),
        (
            # vertex_list
            [],  # empty graph!
            # edge_list
            [],
            # encoding
            "clique", # in clique-encoding
        ),
        (
            # vertex_list
            [],  # empty graph!
            # edge_list
            [],
            # encoding
            "direct",  # in direct-encoding
        ),
        (
            #  V1---V2
            #  |
            #  V3   V4
            #
            # vertex_list
            [1,2,3,4],
            # edge_list
            [
                (1,2),
                (1,3),  # one isolated vertex
            ],
            # encoding
            "edge",     # in edge-encoding
        ),
        (
            #  V1---V2
            #  |
            #  V3   V4
            #
            # vertex_list
            [1,2,3,4],
            # edge_list
            [
                (1,2),
                (1,3),  # one isolated vertex
            ],
            # encoding
            "clique",     # in clique-encoding
        ),
        (
            #  V1---V2
            #
            # vertex_list
            [1,2],
            # edge_list
            [(1,2)],  # isolated edge
            # encoding
            "direct", # in direct-encoding
        ),
        (
            #  V1    V2
            #
            # vertex_list
            [1,2],
            # edge_list
            [],       # multiple isolated vertices
            # encoding
            "direct", # in direct-encoding
        ),
    ]

    for vertex_list, edge_list, encoding in tests:
        NameMgr.clear()
        st = GrSt(vertex_list,edge_list,encoding=encoding)
        check_grst_object(st, vertex_list, edge_list, encoding)

    # tests over encoding and prefix
    #  V1---V2
    #  |   /
    #  |  /
    #  | /
    #  V3---V5
    #
    # vertex_list
    vertex_list = [2,3,1,5]
    # edge_list
    edge_list = [
        (2,1),
        (3,1),
        (2,3),
        (3,5),
    ]
    for encoding in ["edge", "clique", "direct"]:
        for prefix in ["V", "WW", "V12"]:
            NameMgr.clear()
            st = GrSt(vertex_list,edge_list,encoding=encoding)
            check_grst_object(st, vertex_list, edge_list, encoding)

def check_grst_object(st: GrSt, \
    vertex_list: list, edge_list: list, encoding: str):
    assert st._encoding == encoding
    assert set(vertex_list) == set(st._verts)
    for edge in edge_list:
        assert tuple(sorted(edge)) in st._edges
    for edge in st._edges:
        assert edge in edge_list or tuple([edge[1],edge[0]]) in edge_list

    for v in vertex_list:
        assert st.object_to_vertex(st.vertex_to_object(v)) == v
    for obj in st.domain:
        assert st.vertex_to_object(st.object_to_vertex(obj)) == obj

    for u in st._verts:
        for v in st._verts:
            if tuple(sorted([u,v])) in st._edges:
                assert st.adjacent(\
                        st.vertex_to_object(u), \
                        st.vertex_to_object(v))
            else:
                assert not st.adjacent(\
                        st.vertex_to_object(u), \
                        st.vertex_to_object(v))
            if u == v:
                assert st.equal(\
                        st.vertex_to_object(u), \
                        st.vertex_to_object(v))
            else:
                assert not st.equal(\
                        st.vertex_to_object(u), \
                        st.vertex_to_object(v))

def test_interpretation():
    tests = [
        (
            #  | 1 2
            #--------
            # 1| 1 0
            # 2| 1 1
            # 3| 0 1
            #
            # formula
            "x=y",
            # vertex list
            [1,2,3],
            # edge list
            [(1,2), (2,3)],
            # encoding
            "edge",
            # first symbol
            "x",
            # second symbol
            "V1",
            # expected adjacency between first and second symbols
            "(((x@1 & T) | (x@2 & F)) & (~ ((x@1 <-> T) & (x@2 <-> F))))",
            # expected equality between first and second symbols
            "((x@1 <-> T) & (x@2 <-> F))",
            # expected domain constraint of first symbol
            "(((x@1 & (~ x@2)) | (x@1 & x@2)) | ((~ x@1) & x@2))",
        ),
        (
            #  | 1 2
            #--------
            # 1| 1 0
            # 2| 1 1
            # 3| 0 1
            #
            # formula
            "x=y",
            # vertex list
            [1,2,3],
            # edge list
            [(1,2), (2,3)],
            # encoding
            "edge",
            # first symbol
            "x",
            # second symbol
            "y",
            # expected adjacency between first and second symbols
            "(((x@1 & y@1) | (x@2 & y@2)) & (~ ((x@1 <-> y@1) & (x@2 <-> y@2))))",
            # expected equality between first and second symbols
            "((x@1 <-> y@1) & (x@2 <-> y@2))",
            # expected domain constraint of first symbol
            "(((x@1 & (~ x@2)) | (x@1 & x@2)) | ((~ x@1) & x@2))",
        ),
        (
            #  | 1 2 3
            #---------
            # 1| 1
            # 2|   1
            # 3|     1
            #
            # formula
            "x=y",
            # vertex list
            [1,2,3],
            # edge list
            [(1,2), (2,3)],
            # encoding
            "direct",
            # first symbol
            "x",
            # second symbol
            "V1",
            # expected adjacency between first and second symbols
            "(((x@1 & F) | (x@2 & T)) | ((x@2 & F) | (x@3 & F)))",  # equiv. x@2 & T, meaning x = V2
            # expected equality between first and second symbols
            "(((x@1 <-> T) & (x@2 <-> F)) & (x@3 <-> F))",
            # expected domain constraint of first symbol
            "((((~ (x@1 & x@2)) & (~ (x@1 & x@3))) & (~ (x@2 & x@3))) & ((x@1 | x@2) | x@3))",
        ),
        (
            #  | 1 2 3
            #---------
            # 1| 1
            # 2|   1
            # 3|     1
            #
            # formula
            "x=y",
            # vertex list
            [1,2,3],
            # edge list
            [(1,2), (2,3)],
            # encoding
            "direct",
            # first symbol
            "x",
            # second symbol
            "y",
            # expected adjacency between first and second symbols
            "(((x@1 & y@2) | (x@2 & y@1)) | ((x@2 & y@3) | (x@3 & y@2)))",
            # expected equality between first and second symbols
            "(((x@1 <-> y@1) & (x@2 <-> y@2)) & (x@3 <-> y@3))",
            # expected domain constraint of first symbol
            "((((~ (x@1 & x@2)) & (~ (x@1 & x@3))) & (~ (x@2 & x@3))) & ((x@1 | x@2) | x@3))",
        ),
        (
            #  | 1 2 3
            #---------
            # 1| 1 0 1
            # 2| 1 1 0
            # 3| 0 0 1
            # 4| 0 1 0
            #
            # formula
            "x=y", 
            # vertex list
            [1,2,3,4], 
            # edge list
            [(1,2), (2,4),(1,3)],
            # encoding
            "edge",
            # first symbol
            "x",
            # second symbol
            "y",
            # expected adjacency between first and second symbols
            "((((x@1 & y@1) | (x@2 & y@2)) | (x@3 & y@3)) & (~ (((x@1 <-> y@1) & (x@2 <-> y@2)) & (x@3 <-> y@3))))",
            # expected equality between first and second symbols
            "(((x@1 <-> y@1) & (x@2 <-> y@2)) & (x@3 <-> y@3))",
            # expected domain constraint of first symbol
            "(((((x@1 & (~ x@2)) & x@3) | ((x@1 & x@2) & (~ x@3))) | (((~ x@1) & (~ x@2)) & x@3)) | (((~ x@1) & x@2) & (~ x@3)))",
        ),
        (
            #  | 1 2 3
            #---------
            # 1| 1 0 1
            # 2| 1 1 0
            # 3| 0 0 1
            # 4| 0 1 0
            #
            # formula
            "x=y", 
            # vertex list
            [1,2,3,4], 
            # edge list
            [(1,2), (2,4),(1,3)],
            # encoding
            "direct",
            # first symbol
            "x",
            # second symbol
            "y",
            # expected adjacency between first and second symbols
            "((((x@1 & y@2) | (x@2 & y@1)) | ((x@2 & y@4) | (x@4 & y@2))) | ((x@1 & y@3) | (x@3 & y@1)))",
            # expected equality between first and second symbols
            "((((x@1 <-> y@1) & (x@2 <-> y@2)) & (x@3 <-> y@3)) & (x@4 <-> y@4))",
            # expected domain constraint of first symbol
            "(((((((~ (x@1 & x@2)) & (~ (x@1 & x@3))) & (~ (x@1 & x@4))) & (~ (x@2 & x@3))) & (~ (x@2 & x@4))) & (~ (x@3 & x@4))) & (((x@1 | x@2) | x@3) | x@4))",
        ),
    ]

    NameMgr.clear()

    for test_str, vertex_list, edge_list, encoding, first_var, second_var,\
        expected_edg, expected_eq, expected_domain in tests:
        f = Fog.read(test_str)
        st = GrSt(vertex_list, edge_list, encoding=encoding)

        g = st.encode_edg(\
                    NameMgr.lookup_index(first_var),\
                    NameMgr.lookup_index(second_var)\
        )
        res = op.to_str(g)
        assert res == expected_edg, f"{res}, {expected_edg}"

        g = st.encode_eq(\
                    NameMgr.lookup_index(first_var),\
                    NameMgr.lookup_index(second_var)\
        )
        res = op.to_str(g)
        assert res == expected_eq, f"{res}, {expected_eq}"

        g = st.compute_domain_constraint(NameMgr.lookup_index(first_var))
        res = op.to_str(g)
        assert res == expected_domain, f"{res}, {expected_domain}"
