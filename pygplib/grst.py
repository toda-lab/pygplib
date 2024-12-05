"""Graph relational structure class"""

from typing import overload

from simpgraph import SimpGraph

from .name     import NameMgr
from .symrelst import SymRelSt
from .prop     import Prop
from .fog     import Fog
from .ecc      import Ecc
from . import constraints
from . import op

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
    _VERTEX_ENC = "vertex"
    _DIRECT_ENC = "direct"
    _LOG_ENC    = "log"
    _ENCODING   = (_EDGE_ENC, _CLIQUE_ENC, _VERTEX_ENC, _DIRECT_ENC, _LOG_ENC,)

    def __init__(self, vertex_list: list, edge_list: list, \
                    encoding: str = "edge", prefix: str = "V", ecc = None,\
                    msg: str = ""):
        """Initialize a graph structure.

        Args:
            vertex_list: list of distinct vertices in an arbitrary order
            edge_list: list of distinct edges in an arbitrary order
            encoding: type of encoding ("edge", "clique", "vertex", "direct", "log")
            prefix: prefix of vertex name, which must be uppercase.
            ecc: edge clique cover for clique encoding
            msg: message printed when assertion failed
        """
        if len(vertex_list) == 0:
            raise Exception(f"no vertex given: "+msg)
        for edge in edge_list:
            if len(edge) != 2:
                raise Exception(f"edge must be of size 2: "+msg)
            if edge[0] == edge[1]:
                raise Exception(f"loop is not allowed: "+msg)
            if edge[0] not in vertex_list\
                or edge[1] not in vertex_list:
                raise Exception(f"invalid vertex found: "+msg)
        if encoding not in type(self)._ENCODING:
            raise Exception(f"unsupported encoding type: "+msg)
        if not (prefix.isalpha() and prefix.isupper()):
            raise Exception(\
                "All characters in prefix must be alphabetic and uppercase letters: "+msg)

        self._relation_dict = {
            type(self)._EDGE_ENC:  self._compute_relation_edge_enc,
            type(self)._CLIQUE_ENC:self._compute_relation_clique_enc,
            type(self)._VERTEX_ENC:self._compute_relation_vertex_enc,
            type(self)._DIRECT_ENC:self._compute_relation_direct_enc,
            type(self)._LOG_ENC:   self._compute_relation_log_enc,
        }
        self._be_eq_dict = {
            type(self)._EDGE_ENC:  self._be_eq_arbit_enc,
            type(self)._CLIQUE_ENC:self._be_eq_arbit_enc,
            type(self)._VERTEX_ENC:self._be_eq_arbit_enc,
            type(self)._DIRECT_ENC:self._be_eq_arbit_enc,
            type(self)._LOG_ENC:   self._be_eq_arbit_enc,
        }
        self._be_edg_dict = {
            type(self)._EDGE_ENC:  self._be_edg_edge_enc,
            type(self)._CLIQUE_ENC:self._be_edg_edge_enc,
            type(self)._VERTEX_ENC:self._be_edg_vertex_enc,
            type(self)._DIRECT_ENC:self._be_edg_direct_enc,
            type(self)._LOG_ENC:   self._be_edg_arbit_enc,
            }
        self._be_domain_dict = {
            type(self)._EDGE_ENC:  self._be_domain_arbit_enc,
            type(self)._CLIQUE_ENC:self._be_domain_arbit_enc,
            type(self)._VERTEX_ENC:self._be_domain_vertex_enc,
            type(self)._DIRECT_ENC:self._be_domain_direct_enc,
            type(self)._LOG_ENC:   self._be_domain_log_enc,
        }
        self._be_aux_const_dict = {
            type(self)._EDGE_ENC:  self._compute_auxiliary_constraint_edge_enc,
            type(self)._CLIQUE_ENC:self._compute_auxiliary_constraint_clique_enc,
            type(self)._VERTEX_ENC:self._compute_auxiliary_constraint_vertex_enc,
            type(self)._DIRECT_ENC:self._compute_auxiliary_constraint_direct_enc,
            type(self)._LOG_ENC:   self._compute_auxiliary_constraint_log_enc,
        }

        self._ecc = ecc
        self._domain_enc_dict = {}
        """dictionary of auxiliary Boolean variables for the domain constraint"""
        self._domain_dec_dict = {} 
        """Inverse mapping of _domain_enc_dict"""
        self._edg_enc_dict = {}
        """dictionary of auxiliary Boolean variables for the edg relation"""
        self._edg_dec_dict = {} 
        """Inverse mapping of _edg_enc_dict"""
        self._le_enc_dict = {}
        """dictionary of auxiliary Boolean variables for the order relation"""
        self._le_dec_dict = {} 
        """Inverse mapping of _le_enc_dict"""
        self._encoding = encoding
        """encoding type"""
        self._prefix   = prefix
        """prefix of vertex name"""
        self._vertex_to_index_dict = {}
        self._index_to_vertex_dict = {}
        for vertex in vertex_list:
            i = NameMgr.lookup_index(self._prefix + f"{vertex}")
            self._vertex_to_index_dict[vertex] = i 
            self._index_to_vertex_dict[i] = vertex
        self._verts = tuple(vertex_list)
        """vertices"""
        self._edges = tuple([tuple(sorted(edge)) for edge in edge_list])
        """edges"""
        if len(set(self._verts)) != len(vertex_list):
            raise Exception(f"duplicate vertex found: "+msg)
        if len(set(self._edges)) != len(edge_list):
            raise Exception(f"duplicate edge found: "+msg)
        # vertex_to_object() and object_to_vertex() are now available!
        objects = self.vertex_to_object(self._verts)
        relation = self._relation_dict[self._encoding]()
        super().__init__(objects, relation,msg=msg)
        assert self.code_length > 0
        self._G = SimpGraph()
        for v in objects:
            self._G.add_vertex(v)
        for v,w in self.vertex_to_object(self._edges):
            self._G.add_edge(v,w)
        if len(objects) > 0:
            self.max_v = objects[0]
            for v in objects[1:]:
                if self.lt(self.max_v, v):
                    self.max_v = v

    def _out_neighborhood(self, v: int):
        assert v in self.domain
        return tuple([w for w in self.domain
            if self._object_to_pos(w)+1 in self.get_code(v) and v != w])

    def _in_neighborhood(self, v: int):
        assert v in self.domain
        return tuple([w for w in self.domain
            if self._object_to_pos(v)+1 in self.get_code(w) and v != w])

    def _compute_relation_edge_enc(self):
        return self.vertex_to_object(self._edges)

    def _compute_relation_clique_enc(self):
        if self._ecc is None:
            return self.vertex_to_object(
                Ecc(self._verts, self._edges).compute_separating_ecc())
        else:
            return self.vertex_to_object(self._ecc)

    def _compute_relation_vertex_enc(self):
        pos_dict = {}
        in_neigh_dict = {}
        for i,v in enumerate(self._verts):
            pos_dict[v] = i
            in_neigh_dict[v] = {v}
        for v,w in self._edges:
            if pos_dict[v] < pos_dict[w]:
                v,w = w,v
            assert pos_dict[v] > pos_dict[w]
            in_neigh_dict[v].add(w)
        res = []
        for v in self._verts:
            res.append(tuple(sorted(in_neigh_dict[v])))
        return self.vertex_to_object(tuple(res))

    def _compute_relation_direct_enc(self):
        return self.vertex_to_object(tuple([(v,) for v in self._verts]))

    def _compute_relation_log_enc(self):
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
        return self.vertex_to_object(tuple(res))

    def vertex_to_object_int(self, vertex: int) -> int:
        """Converts vertex to object (constant symbol index).

        Args:
            vertex: a domain object (a constant symbol index)
        Returns:
            a domain object (a constant symbol index)
        """
        if vertex not in self._verts:
            raise Exception(f"invalid vertex: {vertex}")
        return self._vertex_to_index_dict[vertex]

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
        return self._index_to_vertex_dict[obj]

    def adjacent(self, x: int, y: int) -> bool:
        """Determines if constants (meaning vertices) are adjacent.

        Args:
            x: constant symbol index (meaning vertex)
            y: constant symbol index (meaning vertex)
        Returns:
            True if adjacent, and False otherwise.
        """
        if x not in self.domain:
            raise Exception(f"{x} is not a domain object.")
        if y not in self.domain:
            raise Exception(f"{y} is not a domain object.")
        return x in self._G.adj_vertices(y)

    def equal(self, x: int, y: int) -> bool:
        """Determines if constants (meaning vertices) are equal with each other.

        Args:
            x: constant symbol index (meaning vertex)
            y: constant symbol index (meaning vertex)
        Returns:
            True if equal, and False otherwise.
        """
        if x not in self.domain:
            raise Exception(f"{x} is not a domain object.")
        if y not in self.domain:
            raise Exception(f"{y} is not a domain object.")
        return x == y

    def lt(self, x: int, y: int) -> bool:
        """Determines if x is less than y in an internal order of vertices.

        Args:
            x: constant symbol index (meaning vertex)
            y: constant symbol index (meaning vertex)
        Returns:
            True if x is less than y, and False otherwise.
        """
        px = self._get_lit_list(x)
        py = self._get_lit_list(y)
        for i in range(self.code_length):
            i = self.code_length-i-1
            assert px[i] in [Prop.true_const(), Prop.false_const()]
            assert py[i] in [Prop.true_const(), Prop.false_const()]
            if px[i] == py[i]:
                continue
            if px[i] == Prop.false_const() and py[i] == Prop.true_const():
                return True
            if px[i] == Prop.true_const()  and py[i] == Prop.false_const():
                return False
        return False

    def sorted(self, li: list) -> None:
        """Sorts list of constants (i.e. vertices) in an increasing order.

        Args:
            li: list of constant indices

        Returns:
            Sorted list
        """
        res = list(li)
        n   = len(res)
        # selection sort based on the order defined by self.lt
        for i in range(n):
            minpos = i
            minval = res[i]
            for j in range(i+1,n):
                if self.lt(res[j],minval):
                    minpos = j
                    minval = res[j]
            tmp      = res[i]
            res[i]   = minval
            res[minpos] = tmp
        # check sorted
        for i in range(n-1):
            assert self.lt(res[i],res[i+1]) or self.equal(res[i],res[i+1])
        return res

    def _get_lit_list(self, x: int) -> list[Prop]:
        """Gets list of literals, given a symbol index.

        Args:
            x: symbol index (constant symbol or variable symbol)
        Returns:
            list of literals (Boolean variables' objects of Prop class)
        """
        if x in self.domain:
            return [Prop.true_const() if i+1 in self.get_code(x) \
                        else Prop.false_const() \
                            for i in range(self.code_length)]
        else:
            return [Prop.var(p) for p in self.get_boolean_var_list(x)]

    def encode_eq(self, x: int, y: int) -> Prop:
        """Encodes predicate of equality relation, given two symbols.

        Args:
            x: symbol index (constant symbol or variable symbol)
            y: symbol index (constant symbol or variable symbol)
        Returns:
            formula object of Prop class
        """
        warn_msg = "`encode_eq()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.be_eq(x,y)

    def be_eq(self, x: int, y: int) -> Prop:
        """Encodes predicate of equality relation, given two symbols.

        Args:
            x: symbol index (constant symbol or variable symbol)
            y: symbol index (constant symbol or variable symbol)
        Returns:
            formula object of Prop class
        """
        return self._be_eq_dict[self._encoding](x,y)

    def _be_eq_arbit_enc(self, x: int, y: int) -> Prop:
        px = self._get_lit_list(x)
        py = self._get_lit_list(y)
        li = [Prop.iff(px[i],py[i]) for i in range(self.code_length)]
        return Prop.binop_batch(Prop.get_land_tag(), li)

    def encode_edg(self, x: int, y: int) -> Prop:
        """Encodes predicate of adjacency relation, given two symbols.

        Args:
            x: symbol index (constant symbol or variable symbol)
            y: symbol index (constant symbol or variable symbol)
        Returns:
            formula object of Prop class
        """
        warn_msg = "`encode_eq()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.be_edg(x,y)

    def be_edg(self, x: int, y: int) -> Prop:
        """Encodes predicate of adjacency relation, given two symbols.

        Args:
            x: symbol index (constant symbol or variable symbol)
            y: symbol index (constant symbol or variable symbol)
        Returns:
            formula object of Prop class
        """
        return self._be_edg_dict[self._encoding](x,y)

    def _be_edg_edge_enc(self, x: int, y: int) -> Prop:
        px = self._get_lit_list(x)
        py = self._get_lit_list(y)
        li = [Prop.land(px[i],py[i]) for i in range(self.code_length)]
        return Prop.land(Prop.neg(self.be_eq(x,y)),
            Prop.binop_batch(Prop.get_lor_tag(), li))

    def _be_edg_direct_enc(self, x: int, y: int) -> Prop:
        px = self._get_lit_list(x)
        py = self._get_lit_list(y)
        li = [Prop.lor(
                Prop.land(
                    px[self._object_to_pos(v)],
                    py[self._object_to_pos(w)]),
                Prop.land(
                    px[self._object_to_pos(w)],
                    py[self._object_to_pos(v)]))
                    for v,w in self._G.all_edges()]
        if len(li) == 0:
            return Prop.false_const()
        else:
            return Prop.land(Prop.neg(self.be_eq(x,y)),
                Prop.binop_batch(Prop.get_lor_tag(), li))

    def _be_edg_arbit_enc(self, x: int, y: int) -> Prop:
        li = [Prop.lor(
                Prop.land(
                    self.be_eq(x,v),
                    self.be_eq(y,w)),
                Prop.land(
                    self.be_eq(x,w),
                    self.be_eq(y,v)))
                    for v,w in self._G.all_edges()]
        if len(li) == 0:
            return Prop.false_const()
        else:
            return Prop.land(Prop.neg(self.be_eq(x,y)),
                Prop.binop_batch(Prop.get_lor_tag(), li))

    def _be_edg_vertex_enc(self, x: int, y: int) -> Prop:
        def _aux_index(x: int, i: int) -> int:
            if (x,i) not in self._edg_enc_dict:
                v = NameMgr.get_aux_index()
                assert v not in self._edg_dec_dict
                self._edg_enc_dict[(x,i)] = v
                self._edg_dec_dict[v] = (x,i)
            return self._edg_enc_dict[(x,i)]
        px = self._get_lit_list(x)
        py = self._get_lit_list(y)
        sx = [Prop.var(_aux_index(x,i))
                    for i in range(self.code_length)]
        sy = [Prop.var(_aux_index(y,i))
                    for i in range(self.code_length)]
        sx.append(Prop.false_const())
        sy.append(Prop.false_const())
        li = [
            Prop.binop_batch(Prop.get_land_tag(),
                [px[i],py[i],Prop.lor(Prop.neg(sx[i-1]),Prop.neg(sy[i-1]))])
            for i in range(self.code_length)]
        return Prop.land(Prop.neg(self.be_eq(x,y)),
                Prop.binop_batch(Prop.get_lor_tag(), li))

    def be_lt(self, x: int, y: int) -> Prop:
        """Encodes predicate of less-than relation, given two symbols.

        Args:
            x: symbol index (constant symbol or variable symbol)
            y: symbol index (constant symbol or variable symbol)
        Returns:
            formula object of Prop class
        """
        def _aux_index(x: int, y: int, i: int) -> int:
            if (x,y,i) not in self._le_enc_dict:
                v = NameMgr.get_aux_index()
                assert v not in self._le_dec_dict
                self._le_enc_dict[(x,y,i)] = v
                self._le_dec_dict[v] = (x,y,i)
            return self._le_enc_dict[(x,y,i)]
        px = self._get_lit_list(x)
        py = self._get_lit_list(y)
        sx = [Prop.var(_aux_index(x,y,i))
                    for i in range(self.code_length)]
        sx.append(Prop.false_const())
        li = [
            Prop.land(
                Prop.implies(
                    Prop.neg(sx[i]),
                    Prop.iff(px[i],py[i])),
                Prop.iff(
                    sx[i],
                    Prop.lor(
                        sx[i+1],
                        Prop.land(Prop.neg(px[i]),py[i]))))
            for i in range(self.code_length)]
        li.append(Prop.iff(sx[0],Prop.true_const()))
        return Prop.binop_batch(Prop.get_land_tag(), li)

    def encode_T(self) -> Prop: 
        """Encodes true constant object of Fog class to Prop object."""
        warn_msg = "`encode_T()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.be_T()

    def be_T(self) -> Prop: 
        """Encodes true constant object of Fog class to Prop object."""
        return Prop.true_const()

    def encode_F(self) -> Prop:
        """Encodes false constant object of Fog class to Prop object."""
        warn_msg = "`encode_F()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.be_F()

    def be_F(self) -> Prop:
        """Encodes false constant object of Fog class to Prop object."""
        return Prop.false_const()

    def compute_auxiliary_constraint(self, f: Fog) -> Prop:
        """Auxiliary constraint encoder

        Args:
            f: a first-order formula object of Fog class
        Returns:
            formula object of Prop class
        """
        return self._be_aux_const_dict[self._encoding](f)
  
    def _compute_auxiliary_constraint_direct_enc(self, f:Fog) -> Prop:
        return Prop.true_const()

    def _compute_auxiliary_constraint_log_enc(self, f:Fog) -> Prop:
        return Prop.true_const()

    def _compute_auxiliary_constraint_edge_enc(self, f:Fog) -> Prop:
        return Prop.true_const()

    def _compute_auxiliary_constraint_clique_enc(self, f:Fog) -> Prop:
        return Prop.true_const()

    def _compute_auxiliary_constraint_vertex_enc(self, f:Fog) -> Prop:
        def _aux_index(x: int, i: int) -> int:
            if (x,i) not in self._edg_enc_dict:
                v = NameMgr.get_aux_index()
                assert v not in self._edg_dec_dict
                self._edg_enc_dict[(x,i)] = v
                self._edg_dec_dict[v] = (x,i)
            return self._edg_enc_dict[(x,i)]
        # find all edg(x,y) occurring in f, wherre x and y are free variables
        # or constants.
        edg_set = set()
        for i, g in op.generate_subformulas(f):
            if i == 0:
                if g.is_edg_atom():
                    # edg(x,y)
                    x = g.get_atom_arg(1)
                    y = g.get_atom_arg(2)
                    edg_set.add((x,y))
        # compute all auxiliary constraints.
        li = []
        for x,y in edg_set:
            px = self._get_lit_list(x)
            py = self._get_lit_list(y)
            sx = [Prop.var(_aux_index(x,i))
                        for i in range(self.code_length)]
            sy = [Prop.var(_aux_index(y,i))
                        for i in range(self.code_length)]
            sx.append(Prop.false_const())
            sy.append(Prop.false_const())
            li += [
                Prop.iff(
                    sx[i],
                    Prop.lor(sx[i-1],Prop.land(Prop.neg(sx[i-1]),px[i])))
                for i in range(self.code_length)]
            li += [
                Prop.iff(
                    sy[i],
                    Prop.lor(sy[i-1],Prop.land(Prop.neg(sy[i-1]),py[i])))
                for i in range(self.code_length)]
        return Prop.binop_batch(Prop.get_land_tag(), li) 

    def compute_domain_constraint(self, x: int) -> Prop:
        """Domain constraint encoder

        Args:
            x: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        return self._be_domain_dict[self._encoding](x)

    def _be_domain_arbit_enc(self, x: int) -> Prop:
        """Domain constraint encoder for arbitrary encoding.

        Args:
            x: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        li = [self.be_eq(x,v) for v in self.domain]
        return Prop.binop_batch(Prop.get_lor_tag(), li)

    def _be_domain_direct_enc(self, x: int) -> Prop:
        """Domain constraint encoder for direct-encoding.

        Args:
            x: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        li = self.get_boolean_var_list(x)
        return Prop.land(
                Prop.binop_batch(Prop.get_lor_tag(), list(map(Prop.var,li))),
                Prop.read(constraints.at_most_r(li, r=1)))

    def _be_domain_log_enc(self, x: int) -> Prop:
        """Domain constraint encoder for log-encoding.

        Args:
            x: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        return Prop.lor(self.be_lt(x, self.max_v), self.be_eq(x, self.max_v))

    def _be_domain_vertex_enc(self, x: int) -> Prop:
        """Domain constraint encoder for vertex-encoding.

        Args:
            x: index of a first-order variable symbol
        Returns:
            formula object of Prop class
        """
        def _aux_index(x: int, i: int) -> int:
            if (x,i) not in self._domain_enc_dict:
                v = NameMgr.get_aux_index()
                assert v not in self._domain_dec_dict
                self._domain_enc_dict[(x,i)] = v
                self._domain_dec_dict[v] = (x,i)
            return self._domain_enc_dict[(x,i)]
        def _conjunction_out_neighborhood(v: int, px: list) -> Prop:
            N = self._out_neighborhood(v)
            if len(N) == 0:
                return Prop.true_const()
            else:
                return Prop.binop_batch(Prop.get_land_tag(),
                    [px[self._object_to_pos(w)] for w in N])
        def _disjunction_in_neighborhood(v: int, px: list, sx: list) -> Prop:
            N = self._in_neighborhood(v)
            if len(N) == 0:
                return Prop.false_const()
            else:
                return Prop.binop_batch(Prop.get_lor_tag(),
                    [Prop.land(px[self._object_to_pos(w)],
                        sx[self._object_to_pos(w)]) for w in N])
        px = self._get_lit_list(x)
        sx = [Prop.var(_aux_index(x,i))
                    for i in range(self.code_length)]
        res = Prop.read(constraints.at_most_r(
            [_aux_index(x,i) for i in range(self.code_length)], r=1))
        li = [Prop.binop_batch(Prop.get_lor_tag(), sx), res]
        li += [Prop.implies(sx[i],px[i]) for i in range(self.code_length)]
        li += [Prop.implies(
                Prop.land(px[self._object_to_pos(v)],
                    sx[self._object_to_pos(v)]),
                _conjunction_out_neighborhood(v,px))
                for v in self._G.all_vertices()]
        li += [Prop.implies(
                Prop.land(px[self._object_to_pos(v)],
                    Prop.neg(sx[self._object_to_pos(v)])),
                _disjunction_in_neighborhood(v,px,sx))
                for v in self._G.all_vertices()]
        return Prop.binop_batch(Prop.get_land_tag(), li)
