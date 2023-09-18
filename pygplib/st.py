"""Relational structure class"""

from pygplib.name import NameMgr


class RelSt:
    """Relational structure to interprete formulas and index-mapping."""

    def get_interpretation_of_assign(self, assign: tuple[int])\
        -> dict[int,int]:
        """Gets interpretation of assignments of propositional variables.

        Args:
            assign: assignments of propositional variables

        Returns:
           dict: associating variable symbol index with element index
        """
        pass

    def get_constant_symbol_tuple(self) -> tuple:
        """Returns a tuple of constant symbol indices.

        Note:
            For each i, the i-th value in the returned tuple represents a
            constant symbol index of the i-th element of domain, where i
            ranges from 0 to domain size-1.
        """
        pass

    def get_domain_size(self) -> int:
        """Returns number of elements in domain."""
        pass

    def get_code_length(self) -> int:
        """Returns code length."""
        pass

    def get_code(self, i: int) -> tuple:
        """Returns the binary code of an index of constant symbol.

        Args:
            i: constant symbol index
        """
        pass

    def get_prop_var(self, i: int, pos: int) -> int:
        """Returns prop. variable index, given symbol index and code position.

        Args:
            i: variable or constant symbol index
            pos: code position ranging from 0 to the code length minus 1.
        """
        if not NameMgr.has_name(i):
            raise ValueError(f"{i} has no name")
        if "@" in NameMgr.lookup_name(i):
            raise Exception(\
            f"The name {NameMgr.lookup_name(i)} of {i} should not include @")
        if not 0 <= pos < self.get_code_length():
            raise IndexError(\
                f"Position must range from 0 to {self.get_code_length()-1}")

        name = NameMgr.lookup_name(i) + "@" + str(pos+1)
        return NameMgr.lookup_index(name)

    def get_prop_var_list(self, i: int) -> list:
        """Returns list of prop. variable indices, given symbol index.

        Args:
            i: variable or constant symbol index

        Returns:
            list: returns list of propositional variable indices
        """
        return [self.get_prop_var(i, pos) for pos in\
            range(self.get_code_length())]

    def get_symbol_index(self, k: int) -> int:
        """Returns symbol index, given propositional variable index.

        Args:
            k: propositional variable index

        Returns:
            int: variable or constant symbol index
        """
        if not self.exists_symbol(k):
            raise ValueError(f"No symbol is linked to {k}")

        name = NameMgr.lookup_name(k)
        res = name.split("@")
        return NameMgr.lookup_index(res[0])

    def get_code_pos(self, k: int) -> int:
        """Returns code position, given propositional variable index.

        Args:
            k: propositional variable index

        Returns:
            int: code position ranging from 0 to the code length minus 1.
        """
        if not self.exists_symbol(k):
            raise ValueError(f"No symbol is linked to {k}")

        name = NameMgr.lookup_name(k)
        res = name.split("@")
        return int(res[1])-1

    def exists_symbol(self, k: int) -> bool:
        """Answers whether there exists symbol index, given prop. var. index.

        Args:
            k: propositional variable index

        Returns:
            bool: returns True if there exists i s.t. k == get_prop_var(i, j).
        """
        name = NameMgr.lookup_name(k)
        res = name.split("@")
        return len(res) == 2 and NameMgr.has_index(res[0]) and res[1].isdigit()

    def exists_prop_var(self, i: int, pos: int) -> bool:
        """Answers whether there exists prop. var k, given symbol index and pos.

        Args:
            i: variable or constant symbol index
            pos: code position ranging from 0 to the code length minus 1.

        Returns:
            bool: returns True if there exists k s.t. k == get_prop_var(i, pos).
        """
        if not NameMgr.has_name(i):
            raise ValueError(f"No symbol is linked to {i}")

        name = NameMgr.lookup_name(i) + "@" + str(pos+1)
        return NameMgr.has_index(name)
