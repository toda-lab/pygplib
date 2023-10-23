"""Class of Symmetric Relational Structure over a single domain of discourse"""

from .name import NameMgr
from .be   import Be

class SymRelSt(Be):
    """Base class of symmetric relational structure.

    All relations are considered to be symmetric.
    Variables run over a single domain of discourse.
    There is no function symbol.
    """

    def __init__(self, objects: tuple[int], relation: tuple[tuple[int]]):
        """Initializes an object of SymRelSt class.

        Initializes a structure so that each object in domain of discourse is 
        assigned a unique code.
        How atomic predicates are interpreted based on the codes should be 
        implemented individually in classes derived from this class.

        ::

                      | 1 2 3 
            ----------|-------
            objects[0]| 0 0 0 
            objects[1]| 1 0 1
            objects[2]| 1 1 0
            objects[3]| 0 1 1 

            relation = (\
                (objects[1],objects[2]),\
                (objects[2],objects[3]),\
                (objects[1],objects[3]),\
            )

            _codes = (\
                (),
                (1,3),
                (1,2),
                (2,3),
            )

            _pos = {\
                objects[0] : 0,
                objects[1] : 1,
                objects[2] : 2,
                objects[3] : 3,
                () : 0,
                (1,3) : 1,
                (1,2) : 2,
                (2,3) : 3,
            }

        Args:
            objects: a domain of discource, a tuple of constant symbol indices
            relation: a tuple of relation instances
        """
        if len(objects) != len(set(objects)):
            raise Exception(f"duplicate object found: {objects}")
        for obj in objects:
            if not NameMgr.has_name(obj):
                raise ValueError(\
                    f"object {obj}, given as symbol index, has no name.")
            if not NameMgr.is_constant(obj):
                raise ValueError(\
                    f"{NameMgr.lookup_name(obj)} is not a constant symbol.")
        for inst in relation:
            if len(set(inst)) != len(inst):
                raise Exception(f"duplicate objcect found: {inst}")
            if False in list(map(lambda i: i > 0, inst)):
                raise Exception(f"invalid relation instance: {inst}")

        # Public instance variables
        self.domain = objects
        """tuple of objects (constant symbol indices)"""

        # Private instance variables (those regarding code ids are made private)
        self._pos = {}
        """dictionary to find the position of an object or its code"""
        for pos, obj in enumerate(self.domain):
            self._pos[obj] = pos

        for pos, obj in enumerate(self.domain):
            assert self._object_to_pos(obj) == pos

        self._codes = self._compute_dual_hypergraph(relation)
        """tuple of codes"""

        for pos, tup in enumerate(self._codes):
            if tup in self._pos:
                raise Exception(f"the codes of position {self._pos[tup]} "\
                +f"and {pos} coincides: {self._codes}")
            self._pos[tup] = pos

        super().__init__(len(relation))

    def _compute_dual_hypergraph(self, \
            hyperedges: list[list[int]]) -> list[list[int]]:
        """Computes a dual hypergraph.

        Args:
            hyperedges: list of lists of objects

        Returns:
            dual hypergraph

        ::

                      | 1 2 3 4
            ----------|---------
            objects[0]| 1 0 0 1 
            objects[1]| 0 0 0 0
            objects[2]| 1 1 0 1

            hyperedges = [
                [objects[0],objects[2]],
                [objects[2]],
                [],
                [objects[0],objects[2]],
            ]

            res = [
                {1,4},
                {},
                {1,2,4},
            ]

            normalized_res = (
                (1,4),
                (),
                (1,2,4),
            )
        """
        res = [set() for i in range(len(self.domain))]
        for pos, tup in enumerate(hyperedges):
            for obj in tup:
                res[self._object_to_pos(obj)].add(pos+1)
        normalized_res = tuple([tuple(sorted(s)) for s in res])
        return normalized_res

    def _object_to_pos(self, obj: int) -> int:
        """Finds the position of an object."""
        return self._pos[obj]

    def _pos_to_object(self, pos: int) -> int:
        """Finds the object of a position."""
        return self.domain[pos]

    def decode_assignment(self, assign: tuple[int]) -> dict[int, int]:
        """Decodes truth assignment of Boolean variables.

        Args:
            assign: truth assignment of Boolean variables

        Returns:
           dict: assignment of first-order variables to objects

        Note:
            element index ranges from 0 to number of codes minus 1
        """

        var_symb_set = {
            self.get_symbol_index(abs(x)) \
                    for x in assign if self.exists_symbol(abs(x))\
        }

        dic = {}  # dic to find set of code pos of value 1 from symbol index
        for var in var_symb_set:
            for bvar in self.get_boolean_var_list(var):
                if (bvar in assign) and (-bvar in assign):
                    raise Exception(f"Conflicting assign w.r.t {bvar}")
                if bvar in assign:
                    if var not in dic:
                        dic[var] = set()
                    pos = self.get_code_pos(bvar)
                    dic[var].add(pos+1)
                    continue
                if -bvar in assign:
                    continue
                raise Exception("Incomplete assign w.r.t {bvar}")

        result = {}
        for var in var_symb_set:
            if var not in dic:
                dic[var] = set()
            code = tuple(sorted(dic[var]))
            if code not in self._pos:
                raise Exception("No matching element")
            result[var] = self._pos_to_object(self._pos[code])

        return result

    def get_code(self, obj: int) -> tuple:
        """Returns the code of an object (a constant symbol index).

        Args:
            obj: constant symbol index
        """
        if not NameMgr.has_name(obj):
            raise ValueError(f"{obj} has no name")
        if not NameMgr.is_constant(obj):
            raise ValueError(\
                f"{NameMgr.lookup_name(obj)} is not constant symbol")

        return self._codes[self._object_to_pos(obj)]
