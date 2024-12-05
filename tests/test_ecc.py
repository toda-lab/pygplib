import random

from pygplib import Ecc
from simpgraph import SimpGraph
from . import graph

def test_compute_ecc():
    variant = "rr"
    for step in range(100):
        n = 20 # number of vertices
        m = random.randint(0,(n*(n-1))//2) # number of edges
        G = graph.random_graph(n,m,
            reject_isolated_vertex=True,
            reject_isolated_edge=True)
        if G is None:
            continue
        obj = Ecc(list(G.all_vertices()), list(G.all_edges()))
        res = obj.compute_ecc(variant=variant)
        # clique?
        for Q in res:
            assert len(Q) > 0
            for u in Q:
                for v in Q:
                    assert u ==v or u in G.adj_vertices(v)
        # edge cover?
        for v,w in G.all_edges():
            found = False
            for Q in res:
                if v in Q and w in Q:
                    found = True
                    break
            assert found

def test_compute_separating_ecc():
    variant = "rr"
    for step in range(100):
        n = 20 # number of vertices
        m = random.randint(0,(n*(n-1))//2) # number of edges
        G = graph.random_graph(n,m,
            reject_isolated_vertex=True,
            reject_isolated_edge=True)
        if G is None:
            continue
        obj = Ecc(list(G.all_vertices()), list(G.all_edges()))
        res = obj.compute_separating_ecc(variant=variant)
        # separating?
        for u in G.all_vertices():
            for v in G.all_vertices():
                if u == v:
                    continue
                found = False
                for Q in res:
                    if u in Q and v not in Q or v in Q and u not in Q:
                        found = True
                assert found
