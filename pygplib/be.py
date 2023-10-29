"""Class of Boolean encoding of first-order variables"""

from .name import NameMgr


class Be:
    """Class of Boolean encoding of first-order variables

    A first-order variable is encoded with a sequence of Boolean variables of
    fixed-length.
    Each such Boolean variable is registered to NameMgr as name x@i, where x
    is the name of the first-order variable from which the Boolean variable is
    encoded and i is the position.
    """

    def __init__(self, length: int):
        """Initializes an object of Be class"""
        self.code_length = length

    def get_boolean_var(self, i: int, pos: int) -> int:
        """Returns a Boolean variable index, given a symbol index and code pos.

        Args:
            i: variable or constant symbol index
            pos: code position ranging from 0 to the code length minus 1.
        """
        if not NameMgr.has_name(i):
            raise ValueError(f"{i} has no name")
        if "@" in NameMgr.lookup_name(i):
            raise Exception(
                f"The name {NameMgr.lookup_name(i)} of {i} should not include @"
            )
        if not 0 <= pos < self.code_length:
            raise IndexError(
                f"Position must range from 0 to {self.code_length-1}"
            )

        name = NameMgr.lookup_name(i) + "@" + str(pos + 1)
        return NameMgr.lookup_index(name)

    def get_boolean_var_list(self, i: int) -> list[int]:
        """Returns a list of Boolean variable indices, given a symbol index.
        
        Args:
            i: variable or constant symbol index
        """
        return [self.get_boolean_var(i,pos) for pos in range(self.code_length)]

    def get_symbol_index(self, k: int) -> int:
        """Returns symbol index, given Boolean variable index.

        Args:
            k: Boolean variable index

        Returns:
            int: variable or constant symbol index
        """
        if not self.exists_symbol(k):
            raise ValueError(f"No symbol is linked to {k}")

        name = NameMgr.lookup_name(k)
        res = name.split("@")
        return NameMgr.lookup_index(res[0])

    def get_code_pos(self, k: int) -> int:
        """Returns code position, given Boolean variable index.

        Args:
            k: Boolean variable index

        Returns:
            int: code position ranging from 0 to the code length minus 1.
        """
        if not self.exists_symbol(k):
            raise ValueError(f"No symbol is linked to {k}")

        name = NameMgr.lookup_name(k)
        res = name.split("@")
        return int(res[1]) - 1

    def exists_symbol(self, k: int) -> bool:
        """Answers whether there exists symbol index, given Boolean var. index.

        Args:
            k: Boolean variable index

        Returns:
            bool: returns True if for some i, k == get_boolean_var(i, j).
        """
        name = NameMgr.lookup_name(k)
        res = name.split("@")
        return len(res) == 2 and NameMgr.has_index(res[0]) and res[1].isdigit()

    def exists_boolean_var(self, i: int, pos: int) -> bool:
        """Answers whether there is a Boolean var k, given symbol index and pos.

        Args:
            i: variable or constant symbol index
            pos: code position ranging from 0 to the code length minus 1.

        Returns:
            bool: returns True if for some k,  k == get_boolean_var(i, pos).
        """
        if not NameMgr.has_name(i):
            raise ValueError(f"No symbol is linked to {i}")

        name = NameMgr.lookup_name(i) + "@" + str(pos + 1)
        return NameMgr.has_index(name)
