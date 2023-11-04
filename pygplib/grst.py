"""Graph relational structure class"""

from typing import overload

from .name     import NameMgr
from .symrelst import SymRelSt
from .prop     import Prop
from .ecc      import Ecc

class GrSt(SymRelSt):
    """Manages graph structure for interpreting formulas (and index-mapping).

    Attributes:
        _EDGE_ENC: edge-encoding
        _CLIQUE_ENC: clique-encoding
        _DIRECT_ENC: direct-encoding
        _LOG_ENC: log-encoding
        _ENCODING: tuple of available encodings

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
    _EDGE_ENC   = "edge"
    _CLIQUE_ENC = "clique"
    _DIRECT_ENC = "direct"
    _LOG_ENC    = "log"
    _ENCODING   = (_EDGE_ENC, _CLIQUE_ENC, _DIRECT_ENC, _LOG_ENC,)

    def __init__(self, vertex_list: list, edge_list: list, \
                    encoding: str = "edge", prefix: str = "V"):
        """Initialize a graph structure.

        Args:
            vertex_list: list of distinct vertices in an arbitrary order
            edge_list: list of distinct edges in an arbitrary order
            encoding: type of encoding ("edge", "clique", "direct", "log")
            prefix: prefix of vertex name, which must be uppercase.
        """
        for edge in edge_list:
            if len(edge) != 2:
                raise Exception(f"edge must be of size 2: {edge}")
            if edge[0] == edge[1]:
                raise Exception(f"loop is not allowed: {edge}")
            if edge[0] not in vertex_list\
                or edge[1] not in vertex_list:
                raise Exception(f"invalid vertex found: {edge}")
        if encoding not in type(self)._ENCODING:
            raise Exception(f"unsupported encoding type: {encoding}")
        if not (prefix.isalpha() and prefix.isupper()):
            raise Exception(\
                "All characters must be alphabetic and uppercase letters")

        self._encoding = encoding
        """encoding type"""
        self._prefix   = prefix
        """prefix of vertex name"""
        for vertex in vertex_list:
            NameMgr.lookup_index(self._prefix + f"{vertex}")
        self._verts = tuple(vertex_list)
        """vertices"""
        self._edges = tuple([tuple(sorted(edge)) for edge in edge_list])
        """edges"""
        if len(set(self._verts)) != len(vertex_list):
            raise Exception(f"duplicate vertex found: {vertex_list}")
        if len(set(self._edges)) != len(edge_list):
            raise Exception(f"duplicate edge found: {edge_list}")
        # vertex_to_object() and object_to_vertex() are now available!

        objects = self.vertex_to_object(self._verts)
        if self._encoding == type(self)._EDGE_ENC:
            relation = self.vertex_to_object(self._edges)
        elif self._encoding == type(self)._CLIQUE_ENC:
            ecc = Ecc(self._verts, self._edges).compute_separating_ecc()
            relation = self.vertex_to_object(ecc)
        elif self._encoding == type(self)._DIRECT_ENC:
            relation = self.vertex_to_object(tuple([(v,) for v in self._verts]))
        elif self._encoding == type(self)._LOG_ENC:
            relation = self.vertex_to_object(self._compute_log_relation())
        else:
            raise Exception(f"invalid encoding type: {self._encoding}")
        super().__init__(objects, relation)

    def _compute_log_relation(self) -> tuple:
        """Computes relation for log-encoding.

        Computes relation for log-encoding, where each relation instance means
        whether it is possible to divide by a power of 2.

        Returns:
            relation for log-encoding, where each relation instance consists of
            vertices.
        """
        res = []
        N = len(self._verts)
        n = 1
        while n < N:
            res.append(tuple(\
                [self._verts[j] for i in range(1,(N-1)//n+1,2)\
                                for j in range(n*i, min(n*(i+1),N))]\
                                    ))
            n *= 2
        return tuple(res)

    def vertex_to_object_int(self, vertex: int) -> int:
        """Converts vertex to object (constant symbol index).

        Args:
            vertex: a domain object (a constant symbol index)
        Returns:
            a domain object (a constant symbol index)
        """
        if vertex not in self._verts:
            raise Exception(f"invalid vertex: {vertex}")
        name = self._prefix + f"{vertex}" 
        if not NameMgr.has_index(name):
            raise Exception(f"vertex: {vertex} not registered to NameMgr.")
        obj = NameMgr.lookup_index(name)
        return obj

    def vertex_to_object_tuple(self, tup: tuple[int]) -> tuple[int]:
        """Converts vertex to object (constant symbol index).

        Args:
            tup: tuple of (tuples of) vertices
        Returns:
            tuple of (tuples of) domain objects (constant symbol indices)
        """
        if not isinstance(tup, tuple):
            raise TypeError
        return tuple([self.vertex_to_object_int(x) if isinstance(x, int)\
                        else self.vertex_to_object_tuple(x)\
                        for x in tup])

    @overload
    def vertex_to_object(self, x: int) -> int:
        pass

    @overload
    def vertex_to_object(self, x: tuple) -> tuple:
        pass

    def vertex_to_object(self, x):
        """Converts vertex to object (constant symbol index).
        
        Alias of vertex_to_object_int() and vertex_to_object_tuple()
        """
        res = None
        if isinstance(x, int):
            res = self.vertex_to_object_int(x)
        else:
            res = self.vertex_to_object_tuple(x)
        return res

    def object_to_vertex(self, obj: int) -> int:
        """Converts object (constant symbol index) to vertex.

        Args:
            obj: domain object (constant symbol index)
        Returns:
            index of vertex.
        """
        name = NameMgr.lookup_name(obj)
        if not (name.find(self._prefix) == 0 \
            and name[len(self._prefix) :].isdigit()):
            raise Exception(f"{name} is not vertex name")

        return int(name[len(self._prefix) :])

    def adjacent(self, i: int, j: int) -> bool:
        """Determines if constants (meaning vertices) are adjacent.

        Args:
            i: constant symbol index (meaning vertex)
            j: constant symbol index (meaning vertex)
        Returns:
            True if adjacent, and False otherwise.
        """
        if i not in self.domain:
            raise Exception(f"{i} is not a domain object.")
        if j not in self.domain:
            raise Exception(f"{j} is not a domain object.")
        u = self.object_to_vertex(i)
        v = self.object_to_vertex(j)
        return tuple(sorted([u,v])) in self._edges

    def equal(self, i: int, j: int) -> bool:
        """Determines if constants (meaning vertices) are equal with each other.

        Args:
            i: constant symbol index (meaning vertex)
            j: constant symbol index (meaning vertex)
        Returns:
            True if equal, and False otherwise.
        """
        if i not in self.domain:
            raise Exception(f"{i} is not a domain object.")
        if j not in self.domain:
            raise Exception(f"{j} is not a domain object.")
        return i == j

    def _get_lit_list(self, index: int) -> list[Prop]:
        """Gets list of literals, given a symbol index.

        Args:
            index: symbol index (constant symbol or variable symbol)
        Returns:
            list of literals (Boolean variables' objects of Prop class)
        """
        if index in self.domain:
            return [Prop.true_const() if pos+1 in self.get_code(index) \
                        else Prop.false_const() \
                            for pos in range(self.code_length)]
        else:
            return [Prop.var(j) for j in self.get_boolean_var_list(index)]

    def encode_eq(self, i: int, j: int) -> Prop:
        """Encodes predicate of equality relation, given two symbols.

        Args:
            i: symbol index (constant symbol or variable symbol)
            j: symbol index (constant symbol or variable symbol)
        Returns:
            formula object of Prop class
        """
        li = Prop.bitwise_binop(Prop.get_iff_tag(), \
                                self._get_lit_list(i), \
                                self._get_lit_list(j))
        return Prop.binop_batch(Prop.get_land_tag(), li)

    def encode_edg(self, i: int, j: int) -> Prop:
        """Encodes predicate of adjacency relation, given two symbols.

        Args:
            i: symbol index (constant symbol or variable symbol)
            j: symbol index (constant symbol or variable symbol)
        Returns:
            formula object of Prop class
        """
        res = None
        if self._encoding in (type(self)._EDGE_ENC, type(self)._CLIQUE_ENC):
            li = Prop.bitwise_binop(Prop.get_land_tag(), \
                                    self._get_lit_list(i), \
                                    self._get_lit_list(j))
            res = Prop.binop_batch(Prop.get_lor_tag(), li)
            res = Prop.land(res, Prop.neg(self.encode_eq(i,j)))
        elif self._encoding == type(self)._DIRECT_ENC:
            lit_list = [self._get_lit_list(i),self._get_lit_list(j)]
            or_li = [Prop.lor(\
                    Prop.land(\
                        lit_list[0][self._object_to_pos(edge[0])],\
                        lit_list[1][self._object_to_pos(edge[1])]),\
                    Prop.land(\
                        lit_list[0][self._object_to_pos(edge[1])],\
                        lit_list[1][self._object_to_pos(edge[0])]),\
                        )\
                        for edge in self.vertex_to_object(self._edges)]
            res = Prop.binop_batch(Prop.get_lor_tag(), or_li)
        elif self._encoding == type(self)._LOG_ENC:
            or_li = []
            for edge in self.vertex_to_object(self._edges):
                li = Prop.bitwise_binop(Prop.get_iff_tag(), \
                                self._get_lit_list(i), \
                                self._get_lit_list(edge[0]))
                li += Prop.bitwise_binop(Prop.get_iff_tag(), \
                                self._get_lit_list(j), \
                                self._get_lit_list(edge[1]))
                res0 = Prop.binop_batch(Prop.get_land_tag(), li)
                li = Prop.bitwise_binop(Prop.get_iff_tag(), \
                                self._get_lit_list(i), \
                                self._get_lit_list(edge[1]))
                li += Prop.bitwise_binop(Prop.get_iff_tag(), \
                                self._get_lit_list(j), \
                                self._get_lit_list(edge[0]))
                res1 = Prop.binop_batch(Prop.get_land_tag(), li)
                or_li.append(Prop.lor(res0,res1))
            res = Prop.binop_batch(Prop.get_lor_tag(), or_li)
        else:
            raise Exception(f"NotImplementedError")
        return res

    def encode_T(self) -> Prop: 
        """Encodes true constant object of Fog class to Prop object."""
        return Prop.true_const()

    def encode_F(self) -> Prop:
        """Encodes false constant object of Fog class to Prop object."""
        return Prop.false_const()

    def compute_domain_constraint(self, var: int) -> Prop:
        """Computes domain constraint for a first-order variable.

        Args:
            var: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        if not NameMgr.is_variable(var):
            raise Exception(f"symbol index {var} is not a variable symbol")
        res = None
        if self._encoding in (type(self)._EDGE_ENC, type(self)._CLIQUE_ENC):
            res = self._compute_domain_constraint_DNF(var)
        elif self._encoding == type(self)._DIRECT_ENC:
            res = self._compute_domain_constraint_direct_encoding(var)
        elif self._encoding == type(self)._LOG_ENC:
            res = self._compute_domain_constraint_log_encoding(var)
        else:
            raise Exception(f"NotImplementedError")
        return res

    def _compute_domain_constraint_DNF(self, index: int)\
        -> Prop:
        """Computes a constraint in DNF for a given first-order variable
        such that the variable runs over the domain of this structure.

        Args:
            index: a first-order variable index

        Returns:
            Prop: Prop class object of the computed DNF constraint.
        """
        dnf = []
        for obj in self.domain:
            lits = self._get_lit_list(index)
            term = [
                lits[pos] if pos+1 in self.get_code(obj) \
                else Prop.neg(lits[pos]) \
                for pos in range(self.code_length)
            ]
            dnf.append(Prop.binop_batch(Prop.get_land_tag(), term))
        return Prop.binop_batch(Prop.get_lor_tag(), dnf)

    def _compute_domain_constraint_direct_encoding(self, index: int) -> Prop:
        """Computes domain constraint for a first-order variable
        (direct-encoding version).

        Args:
            var: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        if self._encoding != type(self)._DIRECT_ENC:
            raise Exception(\
            f"encoding type {self._encoding} does not match with this method")

        lits = self._get_lit_list(index)
        # at least one constraint
        at_least_one = Prop.binop_batch(Prop.get_lor_tag(), lits)
        # at most one constraint
        term = [Prop.neg(Prop.land(lits[i],lits[j])) \
                    for i in range(len(lits))\
                        for j in range(i+1,len(lits))]
        at_most_one = Prop.binop_batch(Prop.get_land_tag(), term)
        return Prop.land(at_most_one, at_least_one)

    def _compute_domain_constraint_log_encoding(self, index: int) -> Prop:
        """Computes domain constraint for a first-order variable
        (log-encoding version).

        Args:
            var: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        if self._encoding != type(self)._LOG_ENC:
            raise Exception(\
            f"encoding type {self._encoding} does not match with this method")
        smaller_li = [Prop.false_const()]
        greater_li = [Prop.true_const()]

        smaller_li += self._get_lit_list(index)
        greater_li += self._get_lit_list(\
                            self.vertex_to_object(self._verts[-1]))

        acc = []
        while len(smaller_li) > 0:
            if greater_li[0] == Prop.true_const():
                li = [Prop.neg(smaller_li[0])]
                li += Prop.bitwise_binop(Prop.get_iff_tag(),\
                                        smaller_li[1:],\
                                        greater_li[1:])
                acc.append(Prop.binop_batch(Prop.get_land_tag(), li))
            smaller_li = smaller_li[1:]
            greater_li = greater_li[1:]
        res = Prop.binop_batch(Prop.get_lor_tag(), acc)
        return res
