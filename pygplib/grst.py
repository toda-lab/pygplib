"""Graph relational structure class"""

from pygplib.name  import NameMgr
from pygplib.st    import RelSt

class GrSt(RelSt):
    """Manages structure for interpreting formulas (and index-mapping)."""

    def __init__(self, domain: tuple[tuple[int]], prefix: str = "V"):
        """Set domain and initialize structure.

        Each element of a domain is identified with binary code of fixed length.
        The relations such as adjacency relation of vertices and equality
        relation between vertices are interpreted through such binary codes
        in such a way that two vertices are not equal if and only if there is
        a position at which the codes of the vertices differ; two vertices are
        adjacent if and only if they are not equal and there is a position
        at which the codes of the vertices both have value 1.

        Example:
            Example of domain is ((1), (1,2), (2), ()),
            where the 1st element, V1, has code 10, the 2nd element, V2,
            (also the 3rd element, V3) 11, and the 4th element, V4, 00.
            This defines G = (V, E),
            where V = {V1,V2,V3,V4}, E = {{V1,V2}, {V2,V3}}.

        Args:
            domain: domain on which variables run.
            prefix: prefix of constant symbol name.
        """
        if not (prefix.isalpha() and prefix.isupper()):
            raise ValueError(\
                "All characters must be alphabetic and uppercase letters")

        self._M = max([max(li) for li in domain if len(li) > 0]) # code length
        self._N = len(domain) # domain size
        self._prefix = prefix

        self._D = tuple([self._key_to_code(map(lambda x: x-1, li))\
            for li in domain])

        # dictionary to find position of code in self._D
        self._invdict = {}
        for pos, code in enumerate(self._D):
            key = self._code_to_key(code)
            if key in self._invdict:
                raise Exception(f"{key} appear multiple times.")
            self._invdict[key] = pos

        self._V = tuple(\
                [NameMgr.lookup_index(self._prefix + f"{i+1}")\
                    for i in range(self._N)])

    def _key_to_code(self, key: tuple) -> tuple:
        """Converts key to binary code.

        Args:
            key: tuple of code positions, which need not be sorted.

        Returns:
            tuple: returns a tuple of binary values, representing key.
        """
        res = [0]*self._M
        for pos in sorted(key):
            res[pos] = 1
        return tuple(res)

    def _code_to_key(self, code: tuple) -> tuple:
        """Converts binary code to key.

        Args:
            code: tuple of binary values of code length.

        Returns:
            tuple: returns a tuple of code positions of value 1, sorted in
            increasing order.
        """
        res = [i for i, val in enumerate(code) if val == 1]
        return tuple(res)

    def get_interpretation_of_assign(self, assign: tuple[int])\
        -> dict[int,int]:
        """Gets interpretation of assignments of propositional variables.

        Args:
            assign: assignments of propositional variables

        Returns:
           dict: associating variable symbol index with element index

        Note:
            element index ranges from 0 to domain size-1
        """

        symb_index_set = {self.get_symbol_index(abs(x))\
            for x in assign if self.exists_symbol(abs(x))}

        dic = {} # dic to find set of code pos of value 1 from symbol index
        for index in symb_index_set:
            for prop_index in self.get_prop_var_list(index):
                if (prop_index in assign) and (-prop_index in assign):
                    raise Exception(f"Conflicting assign w.r.t {prop_index}")
                if prop_index in assign:
                    if index not in dic:
                        dic[index] = set()
                    pos = self.get_code_pos(prop_index)
                    dic[index].add(pos)
                    continue
                if -prop_index in assign:
                    continue
                raise Exception("Incomplete assign w.r.t {prop_index}")

        result = {}
        for index in symb_index_set:
            if index not in dic:
                dic[index] = set()
            key = tuple(sorted(dic[index]))
            if key not in self._invdict:
                raise Exception("No matching element")
            result[index] = self._invdict[key]

        return result

    def get_constant_symbol_tuple(self) -> tuple:
        """Returns a tuple of constant symbol indices.

        Note:
            For each i, the i-th value in the returned tuple represents a
            constant symbol index of the i-th element of domain, where i
            ranges from 0 to domain size-1.
        """
        return self._V

    def get_domain_size(self) -> int:
        """Returns number of elements in domain."""
        return self._N

    def get_code_length(self) -> int:
        """Returns code length."""
        return self._M

    def get_code_table(self) -> tuple:
        """Returns code table.

        Note:
            For each element index i, the i-th entry of the returned tuple is a
            code of the element, where i ranges from 0 to domain size-1.
        """
        return self._D

    def get_code(self, i: int) -> tuple:
        """Returns the binary code of an index of constant symbol.

        Args:
            i: constant symbol index
        """
        if not NameMgr.has_name(i):
            raise ValueError(f"{i} has no name")
        if not NameMgr.is_constant(i):
            raise ValueError(\
                f"{NameMgr.lookup_name(i)} is not constant symbol")

        name = NameMgr.lookup_name(i)
        if not (name.find(self._prefix) == 0\
            and name[len(self._prefix):].isdigit()):
            raise ValueError(f"{NameMgr.lookup_name(i)} is not element name")

        pos = int(name[len(self._prefix):])-1
        return self._D[pos]
