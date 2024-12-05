import random
from simpgraph import SimpGraph

def random_graph(n: int, m: int, max_retries: int = 10,
    seed: int = None,
    reject_isolated_vertex: bool = False,
    reject_isolated_edge:   bool = False) -> SimpGraph:
    if n < 0 or m < 0 or m > (n*(n-1))//2:
        raise ValueError("number of vertices or number of edges is invalid.")
    if seed is not None:
        random.seed(seed)
    pairs = [(i,j)\
        for i in range(1, n+1)\
            for j in range(i+1, n+1)]
    for step in range(max_retries):
        G = SimpGraph()
        for v in range(1,n+1):
            G.add_vertex(v)
        random.shuffle(pairs)
        for v,w in sorted(pairs[:m]):
            G.add_edge(v,w)
        Graph_Generation_Success = True
        if reject_isolated_vertex:
            for v in G.all_vertices():
                if len(G.adj_vertices(v)) == 0:
                    Graph_Generation_Success = False
                    break
        if reject_isolated_edge:
            for v,w in G.all_edges():
                if len(G.adj_vertices(v)) == 1\
                    and len(G.adj_vertices(w)) == 1:
                    assert w in G.adj_vertices(v)
                    assert v in G.adj_vertices(w)
                    Graph_Generation_Success = False
                    break
        if not Graph_Generation_Success:
            continue
        return G
    return None
