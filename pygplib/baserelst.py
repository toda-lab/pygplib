"""Base Class of Relational Structure over a single domain of discourse"""

from .name import NameMgr
from .be   import Be

class BaseRelSt(Be):
    """Base class of relational structure.

    This class assumes the followings:
    There is no function symbol.
    A first-order variable runs over a single domain of discourse.
    A first-order variable is encoded with a sequence of Boolean variables of
    fixed-length.
    Each object in domain has unique code, represented 
    by a tuple of integers.
    """

    def __init__(self, \
        objects: tuple[int], codes: tuple[tuple[int]], length: int,\
        msg: str = ""):
        """Initializes an object of BaseRelSt class."""
        self.domain = objects
        """tuple of objects (constant symbol indices)"""
        self._codes = codes
        """tuple of codes"""
        self._pos = {}
        """dictionary to find the position of an object or its code"""
        for pos, obj in enumerate(self.domain):
            self._pos[obj] = pos
        for pos, tup in enumerate(self._codes):
            if tup in self._pos:
                raise Exception(f"the codes of position {self._pos[tup]} "\
                +f"and {pos} coincides: {self._codes}: "+msg)
            self._pos[tup] = pos
        super().__init__(length)

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
            self.get_variable_position_pair(abs(x))[0] \
                    for x in assign if self.is_decodable_boolean_var(abs(x))\
        }

        dic = {}  # dic to find set of code pos of value 1 from symbol index
        for x in var_symb_set:
            for px in self.get_boolean_var_list(x):
                if (px in assign) and (-px in assign):
                    raise Exception(f"Conflicting assign w.r.t {px}")
                if px in assign:
                    if x not in dic:
                        dic[x] = set()
                    pos = self.get_variable_position_pair(px)[1]
                    dic[x].add(pos+1)
                    continue
                if -px in assign:
                    continue
                raise Exception(f"Incomplete assign w.r.t {px}: {NameMgr.lookup_name(x)}")

        result = {}
        for x in var_symb_set:
            if x not in dic:
                dic[x] = set()
            code = tuple(sorted(dic[x]))
            if code not in self._pos:
                raise Exception("No matching element")
            result[x] = self._pos_to_object(self._pos[code])

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
