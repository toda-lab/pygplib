import random

from pygplib import GrSt, NameMgr, Fog, Prop
from pygplib import op
from . import solver
from . import graph
from . import tools

def test_vertex_to_object():
    NameMgr.clear()
    for step in range(3):
        n = 5 # number of vertices
        m = random.randint(0,(n*(n-1))//2) # number of edges
        G = graph.random_graph(n,m,
            reject_isolated_vertex=True,
            reject_isolated_edge=True)
        if G is None:
            continue
        vertex_list = list(G.all_vertices())
        edge_list   = list(G.all_edges())
        random.shuffle(vertex_list)
        random.shuffle(edge_list)
        for encoding in ["direct", "log", "vertex", "edge", "clique"]:
            st = GrSt(vertex_list, edge_list, encoding=encoding)
            for v in vertex_list:
                w = st.vertex_to_object(v)
                assert v == st.object_to_vertex(w)
            for w in st.domain:
                v = st.object_to_vertex(w)
                assert w == st.vertex_to_object(v)


def test_domain_direct_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 0 0 0
        # 2| 0 1 0 0
        # 3| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # expected
        ((1,),(2,),(3,),(4,))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 0 0 0
        # 2| 0 1 0 0
        # 3| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # expected
        ((1,),(2,),(3,),(4,))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="direct")
        assert st._codes == st.vertex_to_object(expected)

def test_domain_log_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2
        #   ----
        # 1| 0 0
        # 2| 1 0
        # 3| 0 1
        # 4| 1 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # expected
        ((),(1,),(2,),(1,2))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2
        #   ----
        # 1| 0 0
        # 2| 1 0
        # 3| 0 1
        # 4| 1 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # expected
        ((),(1,),(2,),(1,2))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="log")
        assert st._codes == st.vertex_to_object(expected)

def test_domain_vertex_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 1 1 0
        # 2| 0 1 1 0
        # 3| 0 0 1 1
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # expected
        ((1,2,3),(2,3),(3,4),(4,))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 0 1 0
        # 2| 0 1 1 1
        # 3| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # expected
        ((1,3),(2,3,4),(3,),(4,))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="vertex")
        assert st._codes == st.vertex_to_object(expected)

def test_domain_edge_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 1 0 0
        # 2| 1 0 1 0
        # 3| 0 1 1 1
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # expected
        ((1,2),(1,3),(2,3,4),(4,))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3
        #   ------
        # 1| 1 0 0
        # 2| 0 1 1
        # 3| 1 1 0
        # 4| 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # expected
        ((1,),(2,3),(1,2),(3,))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="edge")
        assert st._codes == st.vertex_to_object(expected)

def test_domain_clique_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3
        #   ------
        # 1| 1 1 0
        # 2| 1 0 0
        # 3| 1 1 1
        # 4| 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # ecc
        ((1,2,3),(1,3),(3,4)),
        # expected
        ((1,2),(1,),(1,2,3),(3,))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3
        #   ------
        # 1| 1 0 0
        # 2| 0 1 1
        # 3| 1 1 0
        # 4| 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # ecc
        ((1,3),(2,3),(2,4)),
        # expected
        ((1,),(2,3),(1,2),(3,))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, ecc, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="clique", ecc=ecc)
        assert st._codes == st.vertex_to_object(expected)

def test__compute_relation_direct_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 0 0 0
        # 2| 0 1 0 0
        # 3| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # expected
        ((1,),(2,),(3,),(4,))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 0 0 0
        # 2| 0 1 0 0
        # 3| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # expected
        ((1,),(2,),(3,),(4,))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="direct")
        res = st._compute_relation_direct_enc()
        assert res == st.vertex_to_object(expected)

def test__compute_relation_edge_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 1 0 0
        # 2| 1 0 1 0
        # 3| 0 1 1 1
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # expected
        ((1,2),(1,3),(2,3),(3,4))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3
        #   ------
        # 1| 1 0 0
        # 2| 0 1 1
        # 3| 1 1 0
        # 4| 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # expected
        ((1,3),(2,3),(2,4))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="edge")
        res = st._compute_relation_edge_enc()
        assert res == st.vertex_to_object(expected)

def test__compute_relation_clique_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3
        #   ------
        # 1| 1 1 0
        # 2| 1 0 0
        # 3| 1 1 1
        # 4| 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # ecc
        ((1,2,3),(1,3),(3,4)),
        # expected
        ((1,2,3),(1,3),(3,4))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3
        #   ------
        # 1| 1 0 0
        # 2| 0 1 1
        # 3| 1 1 0
        # 4| 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # ecc
        ((1,3),(2,3),(2,4)),
        # expected
        ((1,3),(2,3),(2,4))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, ecc, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="clique", ecc=ecc)
        res = st._compute_relation_clique_enc()
        assert res == st.vertex_to_object(expected)

def test__compute_relation_vertex_enc():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 1 1 0
        # 2| 0 1 1 0
        # 3| 0 0 1 1
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # expected
        ((1,),(1,2),(1,2,3),(3,4))
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 0 1 0
        # 2| 0 1 1 1
        # 3| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # expected
        ((1,),(2,),(1,2,3),(2,4))
    ),
    ]
    NameMgr.clear()

    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="vertex")
        res = st._compute_relation_vertex_enc()
        assert res == st.vertex_to_object(expected)

def test__compute_relation_log_enc():
    tests = [
    (
        # 1|00
        # 2|10
        # 3|01
        # 4|11
        #
        # vertex_list
        [1,2,3,4],
        # expected
        ((2,4),(3,4))
    ),
    (
        # 1|0
        # 4|1
        #
        # vertex_list
        [1,4],
        # expected
        ((4,),)
    ),
    (
        # 1|00
        # 4|10
        # 3|01
        #
        # vertex_list
        [1,4,3],
        # expected
        ((4,),(3,))
    ),
    (
        # 1|00
        # 4|10
        # 3|01
        # 2|11
        #
        # vertex_list
        [1,4,3,2],
        # expected
        ((4,2),(3,2))
    ),
    (
        # 1|000
        # 4|100
        # 3|010
        # 2|110
        # 5|001
        #
        # vertex_list
        [1,4,3,2,5],
        # expected
        ((4,2),(3,2),(5,))
    ),
    (
        # 1|000
        # 4|100
        # 3|010
        # 2|110
        # 5|001
        # 7|101
        #
        # vertex_list
        [1,4,3,2,5,7],
        # expected
        ((4,2,7),(3,2),(5,7))
    ),
    (
        # 1|000
        # 4|100
        # 3|010
        # 2|110
        # 5|001
        # 7|101
        # 6|011
        #
        # vertex_list
        [1,4,3,2,5,7,6],
        # expected
        ((4,2,7),(3,2,6),(5,7,6))
    ),
    (
        # 1|000
        # 4|100
        # 3|010
        # 2|110
        # 5|001
        # 7|101
        # 6|011
        # 8|111
        #
        # vertex_list
        [1,4,3,2,5,7,6,8],
        # expected
        ((4,2,7,8),(3,2,6,8),(5,7,6,8))
    ),
    (
        # 1|0000
        # 4|1000
        # 3|0100
        # 2|1100
        # 5|0010
        # 7|1010
        # 6|0110
        # 8|1110
        # 9|0001
        #
        # vertex_list
        [1,4,3,2,5,7,6,8,9],
        # expected
        ((4,2,7,8),(3,2,6,8),(5,7,6,8),(9,))
    ),
    ]
    NameMgr.clear()

    for vertex_list, expected in tests:
        st = GrSt(vertex_list, [], encoding="log")
        res = st._compute_relation_log_enc()
        assert res == st.vertex_to_object(expected)

def test_out_neighborhood():
    tests = [
        (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    3 2 1 4
        #   --------
        # 3| 1 1 1 1 
        # 2| 0 1 1 0
        # 1| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [3,2,1,4],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # out_neighborhood
        {1:(), 2:(1,), 3:(2,1,4), 4:()}
        ),
        (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    3 2 1 4
        #   --------
        # 3| 1 1 1 0
        # 2| 0 1 0 1 
        # 1| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [3,2,1,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # out_neighborhood
        {1:(), 2:(4,), 3:(2,1), 4:()}
        ),
    ]
    NameMgr.clear()
    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="vertex")
        for v in vertex_list:
            assert sorted(st._out_neighborhood(st.vertex_to_object(v)))\
                == sorted(st.vertex_to_object(expected[v])), {f"v={v}"}

def test_in_neighborhood():
    tests = [
        (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        #    1 2 4 3
        #   --------
        # 1| 1 1 0 1
        # 2| 0 1 0 1
        # 4| 0 0 1 1
        # 3| 0 0 0 1
        #
        # vertex_list
        [1,2,4,3],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # in_neighborhood
        {1:(), 2:(1,), 3:(1,2,4), 4:()}
        ),
        (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        #    1 2 3 4
        #   --------
        # 1| 1 0 1 0
        # 2| 0 1 1 1
        # 3| 0 0 1 0
        # 4| 0 0 0 1
        #
        # vertex_list
        [1,2,3,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # in_neighborhood
        {1:(), 2:(), 3:(1,2), 4:(2,)}
        ),
    ]
    NameMgr.clear()
    for vertex_list, edge_list, expected in tests:
        st = GrSt(vertex_list, edge_list, encoding="vertex")
        for v in vertex_list:
            assert sorted(st._in_neighborhood(st.vertex_to_object(v)))\
                == sorted(st.vertex_to_object(expected[v])), f"v={v}"

def test_lt():
    tests = [
    (
        #  1--2
        #  | /
        #  |/
        #  3--4
        #
        # direct-encoding
        #    2 1 4 3
        #   --------
        # 2| 1 0 0 0
        # 1| 0 1 0 0
        # 4| 0 0 1 0
        # 3| 0 0 0 1
        #
        # log-encoding
        #   ----
        # 2| 0 0
        # 1| 1 0
        # 4| 0 1
        # 3| 1 1
        #  
        # vertex-encoding
        #    2 1 4 3
        #   --------
        # 2| 1 1 0 1
        # 1| 0 1 0 1
        # 4| 0 0 1 1
        # 3| 0 0 0 1
        #
        # edge-encoding
        #   --------
        # 2| 1 0 1 0
        # 1| 1 1 0 0
        # 4| 0 0 0 1
        # 3| 0 1 1 1
        #
        # clique-encoding
        #   ------
        # 2| 1 0 0
        # 1| 1 1 0
        # 4| 0 0 1
        # 3| 1 1 1
        #
        # vertex_list
        [2,1,4,3],
        # edge_list
        [(1,2),(1,3),(2,3),(3,4)],
        # ecc
        ((1,2,3),(1,3),(3,4)),
        # expected
        {"direct":(2,1,4,3),
        "log":(2,1,4,3),
        "vertex":(3,1,2,4),
        "edge":(1,2,4,3),
        "clique":(2,1,4,3)}
    ),
    (
        #  1  2
        #  | /|
        #  |/ |
        #  3  4
        #
        # direct-encoding
        #    3 2 1 4
        #   --------
        # 3| 1 0 0 0
        # 2| 0 1 0 0
        # 1| 0 0 1 0
        # 4| 0 0 0 1
        #
        # log-encoding
        #   ----
        # 3| 0 0
        # 2| 1 0
        # 1| 0 1
        # 4| 1 1
        #
        # vertex-encoding
        #    3 2 1 4
        #   --------
        # 3| 1 1 1 0
        # 2| 0 1 0 1
        # 1| 0 0 1 0
        # 4| 0 0 0 1
        #
        # edge-encoding
        #   ------
        # 3| 1 1 0
        # 2| 0 1 1
        # 1| 1 0 0
        # 4| 0 0 1
        #
        # clique-encoding
        #   ------
        # 3| 1 1 0
        # 2| 0 1 1
        # 1| 1 0 0
        # 4| 0 0 1
        #
        # vertex_list
        [3,2,1,4],
        # edge_list
        [(1,3),(2,3),(2,4)],
        # ecc
        ((1,3),(2,3),(2,4)),
        # expected
        {"direct":(3,2,1,4),
        "log":(3,2,1,4),
        "vertex":(1,3,4,2),
        "edge":(1,3,4,2),
        "clique":(1,3,4,2),}
    ),
    ]
    NameMgr.clear()
    for encoding in ["direct", "log", "vertex", "clique"]:
        for vertex_list, edge_list, ecc, expected in tests:
            _test_lt(encoding, vertex_list, edge_list, ecc, expected[encoding])

def _test_lt(encoding, vertex_list, edge_list, ecc, expected):
        st = GrSt(vertex_list, edge_list, encoding=encoding, ecc=ecc)
        res = st.sorted(st.domain)
        # test lt
        assert tuple(map(st.object_to_vertex,res)) == expected,\
            f"enc={encoding},V={vertex_list},E={edge_list},expected={expected}"

def test_adjacent():
    tests = [
        ("direct", False,False),
        ("log",    False,False),
        ("vertex", False,False),
        ("edge",   True, True),
        ("clique", True, True),
     ]
    for step in range(10):
        for encoding,reject_isolated_vertex,reject_isolated_edge in tests:
            _test_adjacent(encoding=encoding,
                reject_isolated_vertex=reject_isolated_vertex,
                reject_isolated_edge=reject_isolated_edge)

def _test_adjacent(encoding: str,
    reject_isolated_vertex: bool,
    reject_isolated_edge: bool):
    NameMgr.clear()
    n = 5 # number of vertices
    m = random.randint(0,(n*(n-1))//2) # number of edges
    G = graph.random_graph(n,m,
        reject_isolated_vertex=reject_isolated_vertex,
        reject_isolated_edge=reject_isolated_edge)
    if G is None:
        return
    vertex_list = list(G.all_vertices())
    edge_list   = list(G.all_edges())
    random.shuffle(vertex_list)
    random.shuffle(edge_list)
    msg  = "V=["+",".join(map(str,vertex_list))+"]"
    msg += ",E=["+",".join(map(str,edge_list))+"]"
    msg += f",encoding={encoding}"
    st = GrSt(vertex_list, edge_list, encoding=encoding, msg=msg)
    for v in vertex_list:
        for w in vertex_list:
            vv = st.vertex_to_object(v)
            ww = st.vertex_to_object(w)
            if (v,w) in edge_list or (w,v) in edge_list:
                assert st.adjacent(vv,ww), msg+f"(v,w)={v},{w}"
                assert st.adjacent(ww,vv), msg+f"(v,w)={v},{w}"
            else:
                assert not st.adjacent(vv,ww), msg+f"(v,w)={v},{w}"
                assert not st.adjacent(ww,vv), msg+f"(v,w)={v},{w}"

def test_be_eq():
    tests = [
        ("direct", False,False),
        ("log",    False,False),
        ("vertex", False,False),
        ("edge",   True, True),
        ("clique", True, True),
     ]
    for step in range(3):
        for encoding,reject_isolated_vertex,reject_isolated_edge in tests:
            _test_be_eq(encoding=encoding,
                reject_isolated_vertex=reject_isolated_vertex,
                reject_isolated_edge=reject_isolated_edge)

def _test_be_eq(encoding: str,
    reject_isolated_vertex: bool,
    reject_isolated_edge: bool):
    NameMgr.clear()
    x = NameMgr.lookup_index("x")
    y = NameMgr.lookup_index("y")
    n = 5 # number of vertices
    m = random.randint(0,(n*(n-1))//2) # number of edges
    G = graph.random_graph(n,m,
        reject_isolated_vertex=reject_isolated_vertex,
        reject_isolated_edge=reject_isolated_edge)
    if G is None:
        return
    vertex_list = list(G.all_vertices())
    edge_list   = list(G.all_edges())
    random.shuffle(vertex_list)
    random.shuffle(edge_list)
    msg  = "V=["+",".join(map(str,vertex_list))+"]"
    msg += ",E=["+",".join(map(str,edge_list))+"]"
    msg += f",encoding={encoding}"
    st = GrSt(vertex_list, edge_list, encoding=encoding, msg=msg)
    for u in st.domain:
        for v in st.domain:
            f = st.be_eq(u, v)
            if u == v:
                solver.assert_satisfiable(f,msg=msg)
            else:
                solver.assert_unsatisfiable(f,msg=msg)

def test_be_edg():
    tests = [
        ("direct", False,False),
        ("log",    False,False),
        ("vertex", False,False),
        ("edge",   True, True),
        ("clique", True, True),
     ]
    for step in range(3):
        for encoding,reject_isolated_vertex,reject_isolated_edge in tests:
            _test_be_edg(encoding=encoding,
                reject_isolated_vertex=reject_isolated_vertex,
                reject_isolated_edge=reject_isolated_edge)

def _test_be_edg(encoding: str,
    reject_isolated_vertex: bool,
    reject_isolated_edge: bool):
    NameMgr.clear()
    x = NameMgr.lookup_index("x")
    y = NameMgr.lookup_index("y")
    n = 5 # number of vertices
    m = random.randint(0,(n*(n-1))//2) # number of edges
    G = graph.random_graph(n,m,
        reject_isolated_vertex=reject_isolated_vertex,
        reject_isolated_edge=reject_isolated_edge)
    if G is None:
        return
    vertex_list = list(G.all_vertices())
    edge_list   = list(G.all_edges())
    random.shuffle(vertex_list)
    random.shuffle(edge_list)
    msg  = "V=["+",".join(map(str,vertex_list))+"]"
    msg += ",E=["+",".join(map(str,edge_list))+"]"
    msg += f",encoding={encoding}"
    st = GrSt(vertex_list, edge_list, encoding=encoding, msg=msg)
    for u in st._G.all_vertices():
       for v in st._G.all_vertices():
            pair = f",(u,v)={st.object_to_vertex(u)},{st.object_to_vertex(v)}"
            f = st.be_edg(u,v)
            f = Prop.land(f, st.compute_auxiliary_constraint(Fog.edg(u,v)))
            if (u,v) in st._G.all_edges() or (v,u) in st._G.all_edges():
                solver.assert_satisfiable(f,msg=msg+pair)
            else:
                solver.assert_unsatisfiable(f,msg=msg+pair)

def test_be_lt():
    tests = [
        ("direct", False,False),
        ("log",    False,False),
        ("vertex", False,False),
        ("edge",   True, True),
        ("clique", True, True),
     ]
    for step in range(3):
        for encoding,reject_isolated_vertex,reject_isolated_edge in tests:
            _test_be_lt(encoding=encoding,
                reject_isolated_vertex=reject_isolated_vertex,
                reject_isolated_edge=reject_isolated_edge)

def _test_be_lt(encoding: str,
    reject_isolated_vertex: bool,
    reject_isolated_edge: bool):
    NameMgr.clear()
    x = NameMgr.lookup_index("x")
    y = NameMgr.lookup_index("y")
    n = 5 # number of vertices
    m = random.randint(0,(n*(n-1))//2) # number of edges
    G = graph.random_graph(n,m,
        reject_isolated_vertex=reject_isolated_vertex,
        reject_isolated_edge=reject_isolated_edge)
    if G is None:
        return
    vertex_list = list(G.all_vertices())
    edge_list   = list(G.all_edges())
    random.shuffle(vertex_list)
    random.shuffle(edge_list)
    msg  = "V=["+",".join(map(str,vertex_list))+"]"
    msg += ",E=["+",".join(map(str,edge_list))+"]"
    msg += f",encoding={encoding}"
    st = GrSt(vertex_list, edge_list, encoding=encoding, msg=msg)
    for u in st._G.all_vertices():
        for v in st._G.all_vertices():
            f = st.be_lt(u,v)
            if st.lt(u,v):
                solver.assert_satisfiable(f,msg=msg)
            else:
                solver.assert_unsatisfiable(f,msg=msg)

def test_be_domain():
    tests = [
        ("direct", False,False),
        ("log",    False,False),
        ("vertex", False,False),
        ("edge",   True, True),
        ("clique", True, True),
     ]
    for step in range(3):
        for encoding,reject_isolated_vertex,reject_isolated_edge in tests:
            _test_be_domain(encoding=encoding,
                reject_isolated_vertex=reject_isolated_vertex,
                reject_isolated_edge=reject_isolated_edge)

def _test_be_domain(encoding: str,
    reject_isolated_vertex: bool,
    reject_isolated_edge: bool):
    NameMgr.clear()
    x = NameMgr.lookup_index("x") # first-order variable
    n = 5 # number of vertices
    m = random.randint(0,(n*(n-1))//2) # number of edges
    G = graph.random_graph(n,m,
        reject_isolated_vertex=reject_isolated_vertex,
        reject_isolated_edge=reject_isolated_edge)
    if G is None:
        return
    vertex_list = list(G.all_vertices())
    edge_list   = list(G.all_edges())
    random.shuffle(vertex_list)
    random.shuffle(edge_list)
    msg  = "V=["+",".join(map(str,vertex_list))+"]"
    msg += ",E=["+",".join(map(str,edge_list))+"]"
    msg += f",encoding={encoding}"
    st = GrSt(vertex_list, edge_list, encoding=encoding, msg=msg)
    px = st.get_boolean_var_list(x)
    f  = st.compute_domain_constraint(x)
    for n in range(2**st.code_length):
        g = f
        code = tuple([i+1 for i in range(st.code_length)\
                    if tools.binary_code(n,st.code_length)[i] == 1])
        for i in range(st.code_length):
            if i+1 in code:
                g = Prop.land(g,Prop.var(px[i]))
            else:
                g = Prop.land(g,Prop.neg(Prop.var(px[i])))
        if code in st._codes:
            solver.assert_satisfiable(g,msg=msg)
        else:
            solver.assert_unsatisfiable(g,msg=msg)
