"""Graph relational structure class"""

import functools

from .name     import NameMgr
from .symrelst import SymRelSt
from .prop     import Prop
from .ecc      import Ecc

class GrSt(SymRelSt):
    """Manages graph structure for interpreting formulas (and index-mapping).

    Example of Usage is as follows.

    ::

        W1---W2
        |   /
        |  /
        | /
        W3---W5

        import pygplib import GrSt, Fog, NameMgr
        vertex_list = [3,1,2,5]
        edge_list   = [(2,1),(1,3),(3,2),(3,5)]
        st = GrSt(vertex_list, edge_list, prefix = "W")
        i = st.vertex_to_object(vertex_list[0])
        assert NameMgr.lookup_name(i) == f"W{vertex_list[0]}"

    """
    def __init__(self, vertex_list: list, edge_list: list, \
                    encoding: str = "edge", prefix: str = "V"):
        """Initialize a graph structure.

        Args:
            vertex_list: list of vertices
            edge_list: list of edges (pairs of vertices)
            encoding: encoding type ("edge", "clique", "direct", "log")
            prefix: prefix of vertex name, which must be uppercase.
        """
        if len(set(vertex_list)) != len(vertex_list):
            raise Exception(f"duplicate vertex found: {vertex_list}")
        for edge in edge_list:
            if len(edge) != 2:
                raise Exception(f"edge must be of size 2: {edge}")
            if edge[0] == edge[1]:
                raise Exception(f"loop is not allowed: {edge}")
            if edge[0] not in vertex_list\
                or edge[1] not in vertex_list:
                raise Exception(f"invalid vertex found: {edge}")
        if not (prefix.isalpha() and prefix.isupper()):
            raise ValueError(\
                "All characters must be alphabetic and uppercase letters")

        self._encoding = encoding
        self._prefix = prefix

        self.verts = \
            tuple([NameMgr.lookup_index(self._prefix + f"{vertex}") \
                                        for vertex in set(vertex_list)])
        self.edges = tuple(self._normalize_edge_list(edge_list))

        if self._encoding == "edge":
            super().__init__(self.verts, self.edges)
        elif self._encoding == "clique":
            super().__init__(self.verts, \
                Ecc(self.verts, self.edges).compute_separating_ecc())
        elif self._encoding == "direct":
            super().__init__(self.verts, \
                tuple([(i+1,) for i in range(len(self.verts))]) \
                )
        elif self._encoding == "log":
            raise Exception("not-yet-implemented")
        else:
            raise Exception(f"invalid encoding type: {self._encoding}")

    def _normalize_edge_list(self, edge_list: list) -> list:
        res = []
        for edge in edge_list:
            i = self.vertex_to_object(edge[0])
            j = self.vertex_to_object(edge[1])
            normalized = tuple(sorted([i,j]))
            if normalized not in res:
                res.append(normalized)
        return res

    def vertex_to_object(self, vertex: int) -> int:
        name = self._prefix + f"{vertex}" 
        if not NameMgr.has_index(name):
            raise Exception(f"invalid vertex: {vertex}")
        return NameMgr.lookup_index(name)

    def object_to_vertex(self, i: int) -> int:
        if not NameMgr.has_name(i):
            raise Exception(f"invalid symbol: {i}")
        if not NameMgr.is_constant(i):
            raise Exception(f"invalid symbol: {i}")

        name = NameMgr.lookup_name(i)
        if not (name.find(self._prefix) == 0 \
            and name[len(self._prefix) :].isdigit()):
            raise ValueError(f"{NameMgr.lookup_name(i)} is not vertex name")

        return int(name[len(self._prefix) :])

    def adjacent(self, i: int, j: int) -> bool:
        if self._encoding in {"edge", "clique"}:
            return True in [k in self.get_code(j) for k in self.get_code(i)]\
                    and not self.equal(i,j)
        if self._encoding == "direct":
            u = self.object_to_vertex(i)
            v = self.object_to_vertex(j)
            return tuple(sorted([u,v])) in self.edges
        else:
            raise Exception(\
                f"encoding type {self._encoding} does not match with this method")

    def equal(self, i: int, j: int) -> bool:
        return self.get_code(i) == self.get_code(j)

    def _get_lit_list(self, i: int) -> list[Prop]:
        if NameMgr.is_constant(i):
            return [Prop.true_const() if pos+1 in self.get_code(i) \
                        else Prop.false_const() \
                            for pos in range(self.code_length)]
        else:
            return [Prop.var(j) for j in self.get_boolean_var_list(i)]

    def encode_eq(self, i: int, j: int) -> Prop:
        li = Prop.bitwise_binop(Prop.get_iff_tag(), \
                                self._get_lit_list(i), \
                                self._get_lit_list(j))
        if Prop.bipartite_order:
            return Prop.binop_batch(Prop.get_land_tag(), li)
        else:
            return functools.reduce(lambda x,y: Prop.land(x,y), li)

    def encode_edg(self, i: int, j: int) -> Prop:
        if self._encoding in {"edge", "clique"}:
            li = Prop.bitwise_binop(Prop.get_land_tag(), \
                                    self._get_lit_list(i), \
                                    self._get_lit_list(j))
            if Prop.bipartite_order:
                res = Prop.binop_batch(Prop.get_lor_tag(), li)
            else:
                res = functools.reduce(lambda x,y: Prop.lor(x,y), li)
            return Prop.land(res, Prop.neg(self.encode_eq(i,j)))
        elif self._encoding == "direct":
            lits = [self._get_lit_list(i),self._get_lit_list(j)]
            li = [Prop.lor(\
                    Prop.land(lits[0][self._object_to_pos(e[0])], \
                        lits[1][self._object_to_pos(e[1])]),\
                    Prop.land(lits[0][self._object_to_pos(e[1])], \
                        lits[1][self._object_to_pos(e[0])]),\
                        ) for e in self.edges]
            if Prop.bipartite_order:
                return Prop.binop_batch(Prop.get_lor_tag(), li)
            else:
                return functools.reduce(lambda x,y: Prop.lor(x,y), li)
        else:
            raise Exception(\
                f"encoding type {self._encoding} does not match with this method")

    def encode_T(self) -> Prop:
        return Prop.true_const()

    def encode_F(self) -> Prop:
        return Prop.false_const()

    def compute_domain_constraint(self, var: int):
        if self._encoding in ["edge", "clique"]:
            return self._compute_domain_constraint_DNF_clique_encoding(var)
        elif self._encoding == "direct":
            return self._compute_domain_constraint_direct_encoding(var)
        elif self._encoding == "log":
            raise Exception
        else:
            raise Exception
            
    def _compute_domain_constraint_DNF_clique_encoding(self, index: int)\
        -> Prop:
        """Computes a constraint in DNF for a given first-order variable
        such that the variable runs over the domain of this structure.

        Note:
            Use this for edge-encoding or clique-encoding.

        Raises:
            Exception: if index is not a variable symbol.

        Args:
            index: a first-order variable index

        Returns:
            Prop: Prop class object of the computed DNF constraint.
        """
        if self._encoding not in {"edge", "clique"}:
            raise Exception(\
            f"encoding type {self._encoding} does not match with this method")
        if not NameMgr.is_variable(index):
            raise Exception(f"symbol index {index} is not a variable symbol")
        dnf = []
        for obj in self.domain:
            lits = self._get_lit_list(index)
            term = [
                lits[pos] if pos+1 in self.get_code(obj) \
                else Prop.neg(lits[pos]) \
                for pos in range(self.code_length)
            ]
            if Prop.bipartite_order:
                dnf.append(Prop.binop_batch(Prop.get_land_tag(), term))
            else:
                dnf.append(functools.reduce(lambda x,y: Prop.land(x,y), term))
        if Prop.bipartite_order:
            return Prop.binop_batch(Prop.get_lor_tag(), dnf)
        else:
            return functools.reduce(lambda a, b: Prop.lor(a, b), dnf)

    def _compute_domain_constraint_direct_encoding(self, index: int):
        if self._encoding != "direct":
            raise Exception(\
            f"encoding type {self._encoding} does not match with this method")
        if not NameMgr.is_variable(index):
            raise Exception(f"symbol index {index} is not a variable symbol")

        lits = self._get_lit_list(index)
        # at least one constraint
        if Prop.bipartite_order:
            at_least_one = Prop.binop_batch(Prop.get_lor_tag(), lits)
        else:
            at_least_one = functools.reduce(lambda x,y: Prop.lor(x,y), lits)
        # at most one constraint
        term = [Prop.neg(Prop.land(lits[i],lits[j])) \
                    for i in range(len(lits))\
                        for j in range(i+1,len(lits))]
        if Prop.bipartite_order:
            at_most_one = Prop.binop_batch(Prop.get_land_tag(), term)
        else:
            at_most_one = functools.reduce(lambda x,y: Prop.land(x,y), term)
        return Prop.land(at_most_one, at_least_one)
