import random
from simpgraph import SimpGraph

class Ecc:
    """Class for computing an edge clique cover.

    The algorithm for computing an edge clique cover is based on heuristic
    algorithms by Conte et al. Please see :
    https://doi.org/10.1016/j.ic.2019.104464
    """

    def __init__(self, vertex_list, edge_list):
        for v in vertex_list:
            if v < 0:
                raise Exception()
        for e in edge_list:
            if type(e) != tuple and len(e) != 2:
                raise Exception()
            if e[0] not in vertex_list or e[1] not in vertex_list:
                raise Exception()
        self._G = SimpGraph()
        """graph"""
        for v in vertex_list:
            self._G.add_vertex(v)
        for v,w in edge_list:
            self._G.add_edge(v,w)
        self._invdic = {}
        """dictionary to find the position of edge or vertex in _G.all_edges"""
        for pos, e in enumerate(self._G.all_edges()):
            assert e not in self._invdic
            self._invdic[e] = pos
        for pos, v in enumerate(self._G.all_vertices()):
            assert v not in self._invdic
            self._invdic[v] = pos
        nof_isolated_verts = 0
        for v in self._G.all_vertices():
            if len(self._G.adj_vertices(v)) == 0:
                nof_isolated_verts += 1
        nof_isolated_edges = 0
        for v,w in self._G.all_edges():
            if len(self._G.adj_vertices(v)) == 1\
                and len(self._G.adj_vertices(w)) == 1:
                nof_isolated_edges += 1
        if nof_isolated_verts > 0:
            raise Exception(f"isolated vertex is not allowed.")
        if nof_isolated_edges > 0:
            raise Exception(f"isolated edge is not allowed.")

    def _select_uncovered_edge(self, U: list, variant: str = "r"):
        """Selects an uncovered edge at random.

        Args:
            U: list of uncovered edges
            variant: "r" if random

        Returns:
            vertices that are incident to the selected edge.
        """
        if variant == "r":
            return random.choice(U)
        else:
            raise Exception(f"NotImplementedError: variant {variant}")

    def _extract_node(self, P: set, Q: list, variant: str = "r")\
        -> int:
        """Extracts a node from a given set of vertices.

        Args:
            P: a set of vertices
            Q: a clique to be constructed
            variant: "r" if random

        Returns:
            int: an extracted vertex if successful: -1 otherwise
        """
        if len(P) == 0:
            return -1

        if variant == "r":
            return random.choice(list(P))
        else:
            raise Exception(f"NotImplementedError: variant {variant}")

    def _find_clique_covering(self, u: int, v:int, U: list, \
        variant: str = "r") -> tuple:
        """Finds a clique convering a given edge.

        Args:
            u: one of the vertices that are adjacent with each other
            v: the other vertex
            U: list of uncovered edges
            variant: variant for the vertex extraction
        """
        Q = [u,v]
        P = set(self._G.adj_vertices(u)) & set(self._G.adj_vertices(v))
        z = self._extract_node(P,Q,variant)
        while z != -1:
            Q.append(z)
            P = P & set(self._G.adj_vertices(z))
            z = self._extract_node(P,Q,variant)
        return tuple(sorted(Q))

    def _mark_all_edges_covered(self, Q: tuple, U: list, p: list) -> None:
        """Marks all edges of Q as covered.

        Update U and p so that all edges in Q are marked as covered.

        Args:
            Q: clique
            U: list of uncovered edges
            p: list to find the position of each edge in U.
        """
        for i in range(len(Q)):
            for j in range(i+1,len(Q)):
                e = tuple(sorted([Q[i],Q[j]]))
                pos = self._invdic[e]
                if not p[pos] < len(U): # e is already covered.
                    continue
                U[p[pos]] = U[-1]
                p[self._invdic[U[-1]]] = p[pos]
                p[pos] = len(U)-1
                U.pop(-1)

    def compute_ecc(self, variant: str = "rr") -> list[list[int]]:
        """Computes an edge clique cover of a given graph."""
        if len(variant) != 2:
            raise Exception(f"variant {variant} not defined")
        # edge clique cover
        C = []
        # edges remaining uncovered
        U = list(self._G.all_edges())
        # list to find the position of each edge in U.
        # U[p[i]] == all_edges[i] holds if the i-th edge remains uncovered.
        p = list(range(len(self._G.all_edges())))
        while U != []:
            (u,v) = self._select_uncovered_edge(U,variant=variant[0])
            Q = self._find_clique_covering(u,v,U,variant=variant[1])
            C.append(Q)
            self._mark_all_edges_covered(Q,U,p)
        return tuple(C)

    def _select_unseparated_block(self, U: list, variant: str = "r"):
        """Selects an unseparated block at random.

        Args:
            U: list of uncovered edges
            variant: "r" if random

        Returns:
            vertices that are incident to the selected edge.
        """
        if variant == "r":
            return random.choice(U)
        else:
            raise Exception(f"NotImplementedError: variant {variant}")

    def _find_clique_separating(self, S: set, variant: str = "r") -> tuple:
        """Finds a clique separating a given block.

        Args:
            S: set of vertices of at least size 2
            variant: variant for the vertex extraction
        """
        assert len(S) >= 2
        u = random.choice(list(S))
        v = random.choice(list(S-{u}))
        # Find a clique separaring u and v.
        if len(self._G.adj_vertices(u)) == 1:
            u,v = v,u
        Q = [u]
        P = set(self._G.adj_vertices(u)) - {v}
        assert len(P) > 0
        z = self._extract_node(P,Q,variant)
        while z != -1:
            assert z != v
            Q.append(z)
            P = P & set(self._G.adj_vertices(z))
            z = self._extract_node(P,Q,variant)
        return tuple(sorted(Q))

    def _separate_blocks(self, Q: tuple, U: list) -> list:
        """Separate blocks by a clique.

        Args:
            Q: clique
            U: list of blocks
        """
        new_U = []
        while U != []:
            S = U.pop()
            T = [set(),set()]
            for w in S:
                if w in Q:
                    T[1].add(w)
                else:
                    T[0].add(w)
            for i in [0,1]: 
                if len(T[i]) > 1:
                    new_U.append(T[i])
        return new_U
           
    def compute_separating_ecc(self, variant: str = "rr") -> list[list[int]]:
        """Computes a separating edge clique cover of a given graph."""
        C = list(self.compute_ecc(variant=variant))
        U = [set(self._G.all_vertices())]
        for Q in C:
            U = self._separate_blocks(Q, U)
        while U != []:
            S = self._select_unseparated_block(U,variant=variant[0])
            Q = self._find_clique_separating(S,variant=variant[1])
            C.append(Q)
            U = self._separate_blocks(Q,U)
        return tuple(C)
