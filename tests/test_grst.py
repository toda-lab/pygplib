from pygplib import GrSt, NameMgr, Fog, Prop
from pygplib import op


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
            # encoding
            "edge",
            # prefix
            "W",
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
                (3,1),
                (2,3),
                (3,5),
            ],
            # encoding
            "clique",
            # prefix
            "W",
        ),
    ]

    for vertex_list, edge_list, encoding, prefix in tests:
        NameMgr.clear()
        st = GrSt(vertex_list,edge_list,encoding=encoding,prefix=prefix)

        for v in vertex_list:
            assert st.object_to_vertex(st.vertex_to_object(v)) == v
        for obj in st.domain:
            assert st.vertex_to_object(st.object_to_vertex(obj)) == obj

        assert st._encoding == encoding
        assert st._prefix == prefix

        assert len(set(vertex_list)) == len(set(st.verts))
        for v in vertex_list:
            assert st.vertex_to_object(v) in st.verts
        for w in st.verts:
            assert st.object_to_vertex(w) in vertex_list

        assert len(set(edge_list)) == len(set(st.edges))
        for e in edge_list:
            f = tuple(sorted(map(lambda v: st.vertex_to_object(v), e)))
            assert f in st.edges 
        for f in st.edges:
            assert (f[1],f[0]) not in st.edges
            e = list(map(lambda w: st.object_to_vertex(w), f))
            assert (e[0],e[1]) in edge_list or (e[1],e[0]) in edge_list

def test__compute_domain_constraint_DNF_clique_encoding():
    tests = [
        #  | 1 2
        #--------
        # 1| 1 0
        # 2| 1 1
        # 3| 0 1
        ("T", [1,2,3], [(1,2), (2,3)], "edge", set()),
        ("! [x] : ? [y] : x=y", [1,2,3], [(1,2), (2,3)], "edge", set()),
        (
            "x=y",
            [1,2,3],
            [(1,2), (2,3)],
            "edge",
            {"(((y@1 & (~ y@2)) | (y@1 & y@2)) | ((~ y@1) & y@2))",\
             "(((x@1 & (~ x@2)) | (x@1 & x@2)) | ((~ x@1) & x@2))"},
        ),
        #  | 1 2
        #--------
        # 1| 1 0
        # 2| 1 1
        # 3| 0 0
        # 4| 0 1
        (
            "x=y", 
            [1,2,3,4], 
            [(1,2), (2,4)], 
            "edge",
            {
            "((((y@1 & (~ y@2)) | (y@1 & y@2)) | ((~ y@1) & (~ y@2))) | ((~ y@1) & y@2))", \
            "((((x@1 & (~ x@2)) | (x@1 & x@2)) | ((~ x@1) & (~ x@2))) | ((~ x@1) & x@2))"
            }),
    ]

    NameMgr.clear()
    Fog.st = None

    for test_str, vertex_list, edge_list, encoding, expected in tests:
        res = Fog.read(test_str)
        st = GrSt(vertex_list, edge_list, encoding=encoding)
        Fog.st = st
        Prop.st = st

        tup = tuple([ \
            st._compute_domain_constraint_DNF_clique_encoding(v) \
                for v in op.get_free_vars(res)])
        res_set = set()
        for i in range(len(tup)):
            res_str = op.to_str(tup[i])
            res_set.add(res_str)
        assert res_set == expected, f"{res_set}, {expected}"

        Fog.st = None
        Prop.st = None
