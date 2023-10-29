import random

class Ecc:
    """Class for computing an edge clique cover.

    The algorithm for computing an edge clique cover is based on heuristic
    algorithms by Conte et al. Please see :
    https://doi.org/10.1016/j.ic.2019.104464
    """

    def __init__(self, vertex_list: list, edge_list: list):
        if len(set(vertex_list)) != len(vertex_list):
            raise Exception(f"duplicate vertex found: {vertex_list}")
        if False in list(map(lambda x: x > 0, vertex_list)):
            raise Exception(f"non-positive index found: {vertex_list}")
        for e in edge_list:
            if len(e) != 2 or e[0] == e[1]:
                raise Exception(f"invalid edge: {e}")
            if e[0] not in vertex_list\
                or e[1] not in vertex_list:
                raise Exception(f"invalid vertex specified by edge: {e}")

        self.verts = tuple(vertex_list)
        """tuple of vertices"""
        self.edges = tuple([tuple(sorted(e)) for e in edge_list])
        """tuple of edges, where each edge is a sorted tuple."""
        self._invdic = {}
        """dictionary to find the position of an edge or vertex in self.edges"""
        for pos, e in enumerate(self.edges):
            assert e not in self._invdic
            self._invdic[e] = pos
        for pos, v in enumerate(self.verts):
            assert v not in self._invdic
            self._invdic[v] = pos
        self._N = {}
        """dictionary to find the neighborhood of a vertex"""
        for e in self.edges:
            if e[0] not in self._N:
                self._N[e[0]] = set()
            self._N[e[0]].add(e[1])
            if e[1] not in self._N:
                self._N[e[1]] = set()
            self._N[e[1]].add(e[0])
        self.nof_isolated_verts = 0
        """number of isolated vertices"""
        for v in self.verts:
            if len(self._N[v]) == 0:
                self.nof_isolated_verts += 1
        self.nof_isolated_edges = 0
        """number of isolated edges"""
        for e in self.edges:
            if len(self._N[e[0]]) == 1 and len(self._N[e[1]]):
                self.nof_isolated_edges += 1

        if self.nof_isolated_verts > 1:
            raise Exception(f"number of isolated vertices must be at most one.")
        if self.nof_isolated_edges > 0:
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
            i = random.randint(0,len(U)-1)
            return U[i][0], U[i][1]
        else:
            raise Exception(f"variant {variant} not yet implemented")

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
            pos = random.randint(0,len(P)-1)
            return list(P)[pos]
        else:
            raise Exception(f"variant {variant} not yet implemented")

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
        P = self._N[u] & self._N[v]
        z = self._extract_node(P,Q,variant)
        while z != -1:
            Q.append(z)
            P = P & self._N[z]
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
                assert e in self._invdic
                pos = self._invdic[e]
                if not p[pos] < len(U): # e is already covered.
                    continue
                U[p[pos]] = U[-1]
                assert U[-1] in self._invdic
                p[self._invdic[U[-1]]] = p[pos]
                p[pos] = len(U)-1
                U.pop(-1)

    def compute_ecc(self, variant: str = "rr") -> list[list[int]]:
        """Computes an edge clique cover of a given graph."""
        if len(variant) != 2:
            raise Exception(f"variant {variant} not defined")
        C = []
        # edge clique cover
        U = [e for e in self.edges]
        # edges remaining uncovered
        p = [pos for pos in range(len(self.edges))]
        # list to find the position of each edge in U.
        # U[p[i]] == self.edges[i] holds if the i-th edge remains uncovered.
        while U != []:
            u,v = self._select_uncovered_edge(U,variant=variant[0])
            Q = self._find_clique_covering(u,v,U,variant=variant[1])
            C.append(Q)
            self._mark_all_edges_covered(Q,U,p)
        return tuple(C)

    def _select_unseparated_edge(self, U: list, variant: str = "r"):
        """Selects an unseparated edge at random.

        Args:
            U: list of uncovered edges
            variant: "r" if random

        Returns:
            vertices that are incident to the selected edge.
        """
        if variant == "r":
            i = random.randint(0,len(U)-1)
            return U[i][0], U[i][1]
        else:
            raise Exception(f"variant {variant} not yet implemented")

    def _find_clique_separating(self, u: int, v:int, U: list, \
        variant: str = "r") -> tuple:
        """Finds a clique separating a given edge.

        Args:
            u: one of the vertices that are adjacent with each other
            v: the other vertex
            U: list of uncovered edges
            variant: variant for the vertex extraction
        """
        if len(self._N[u]) == 1:
            Q = [v]
            P = self._N[v] - {u}
        else:
            Q = [u]
            P = self._N[u] - {v}
        assert len(P) > 0
        z = self._extract_node(P,Q,variant)
        while z != -1:
            Q.append(z)
            P = P & self._N[z]
            z = self._extract_node(P,Q,variant)
        return tuple(sorted(Q))

    def _mark_all_edges_separated(self, Q: tuple, U: list, p: list) -> None:
        """Marks all edges of Q as separated.

        Update U and p so that all edges in Q are marked as separated.

        Args:
            Q: clique
            U: list of unseparated edges
            p: list to find the position of each edge in U.
        """
        for u in Q:
            for v in self._N[u] - set(Q):
                e = tuple(sorted([u,v]))
                assert e in self._invdic
                pos = self._invdic[e]
                if not p[pos] < len(U): # e is already separated.
                    continue
                U[p[pos]] = U[-1]
                assert U[-1] in self._invdic
                p[self._invdic[U[-1]]] = p[pos]
                p[pos] = len(U)-1
                U.pop(-1)

    def compute_separating_ecc(self, variant: str = "rr") -> list[list[int]]:
        """Computes a separating edge clique cover of a given graph."""
        C = list(self.compute_ecc(variant=variant))

        # separating edge clique cover
        M = [set() for v in self.verts]
        # cliques incident to each vertex
        for pos, Q in enumerate(C):
            for v in Q:
                M[self._invdic[v]].add(pos)
        U = [e for e in self.edges \
                if M[self._invdic[e[0]]] == M[self._invdic[e[1]]]]
        # edges remaining unseparated
        p = [pos for pos in range(len(self.edges))]
        # list to find the position of each edge in U.
        # U[p[i]] == self.edges[i] holds if the i-th edge remains unseparated.
        while U != []:
            u,v = self._select_unseparated_edge(U,variant=variant[0])
            assert tuple(sorted([u,v])) in self.edges
            Q = self._find_clique_separating(u,v,U,variant=variant[1])
            C.append(Q)
            self._mark_all_edges_separated(Q,U,p)
        return tuple(C)
