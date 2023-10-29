"""Class of Symmetric Relational Structure over a single domain of discourse"""

from .name import NameMgr
from .baserelst import BaseRelSt

class SymRelSt(BaseRelSt):
    """Class of symmetric relational structure.

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

        super().__init__(\
            objects, \
            type(self)._compute_dual_hypergraph(objects, relation), \
            len(relation))

    @staticmethod
    def _compute_dual_hypergraph(vertices: tuple[int], \
            hyperedges: tuple[tuple[int]]) -> tuple[tuple[int]]:
        """Computes a dual hypergraph.

        Args:
            vertices: tuple of vertices 
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
        index = {}
        for pos, vert in enumerate(vertices):
            index[vert] = pos
        res = [set() for i in range(len(vertices))]
        for pos, tup in enumerate(hyperedges):
            for vert in tup:
                res[index[vert]].add(pos+1)
        normalized_res = tuple([tuple(sorted(s)) for s in res])
        return normalized_res
