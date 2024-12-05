"""Class of Boolean encoding of variables"""

from .name import NameMgr


class Be:
    """Class of Boolean encoding of variables

    A variable is encoded to a sequence of Boolean variables of
    fixed-length.
    """

    def __init__(self, length: int):
        """Initializes an object of Be class"""
        self.code_length = length
        """length of boolean encoding of a variable"""
        self._be_encode_dict = {}
        """dictionary mapping variable-position pair to Boolean variable"""
        self._be_decode_dict = {} 
        """dictionary mapping Boolean variable to variable-position pair"""

    def get_boolean_var(self, i: int, pos: int) -> int:
        """Returns a Boolean encoding of a variable at a given position.

        Args:
            i: index of variable symbol
            pos: code position ranging from 0 to the code length minus 1.

        Returns:
            index of Boolean variable
        """
        if not NameMgr.has_name(i):
            raise ValueError(f"{i} has no name")
        if not NameMgr.is_variable(i):
            raise ValueError(f"{i} is not a variable")
        if not 0 <= pos < self.code_length:
            raise IndexError(
                f"Position must range from 0 to {self.code_length-1}"
            )
        if (i,pos) not in self._be_encode_dict:
            res = NameMgr.get_aux_index()
            assert not self.is_decodable_boolean_var(res)
            self._be_encode_dict[(i,pos)] = res
            self._be_decode_dict[res] = (i,pos)
        return self._be_encode_dict[(i,pos)]

    def get_boolean_var_list(self, i: int) -> list[int]:
        """Returns a Boolean encoding of a variable.
        
        Args:
            i: index of variable symbol

        Returns:
            list of Boolean variables
        """
        return [self.get_boolean_var(i,pos) for pos in range(self.code_length)]

    def get_variable_position_pair(self, k: int) -> tuple[int,int]:
        """Decode a Boolean variable to a variable and a position.

        Args:
            k: index of Boolean variable

        Returns:
            index of a variable symbol and a position
        """
        if not self.is_decodable_boolean_var(k):
            raise ValueError(f"{k} undecodable")
        return self._be_decode_dict[k]

    def is_decodable_boolean_var(self, k: int) -> bool:
        """Is it a decodable Boolean variable?

        Args:
            k: index of Boolean variable

        Returns:
            bool: returns True if for some i, k == get_boolean_var(i, j).

        Note:
            auxiliary propositional variables are not decodable.
        """
        return k in self._be_decode_dict

    def get_symbol_index(self, k: int) -> int:
        """Returns symbol index, given Boolean variable index.

        Args:
            k: Boolean variable index

        Returns:
            int: variable or constant symbol index
        """
        warn_msg = "`get_symbol_index()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.get_variable_position_pair(k)[0]

    def get_code_pos(self, k: int) -> int:
        """Returns code position, given Boolean variable index.

        Args:
            k: Boolean variable index

        Returns:
            int: code position ranging from 0 to the code length minus 1.
        """
        warn_msg = "`get_code_pos()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.get_variable_position_pair(k)[1]

    def exists_symbol(self, k: int) -> bool:
        """Answers whether there exists symbol index, given Boolean var. index.

        Args:
            k: Boolean variable index

        Returns:
            bool: returns True if for some i, k == get_boolean_var(i, j).
        """
        warn_msg = "`exists_symbol()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        raise Exception

    def exists_boolean_var(self, i: int, pos: int) -> bool:
        """Answers whether there is a Boolean var k, given symbol index and pos.

        Args:
            i: variable or constant symbol index
            pos: code position ranging from 0 to the code length minus 1.

        Returns:
            bool: returns True if for some k,  k == get_boolean_var(i, pos).
        """
        warn_msg = "`exists_boolean_var()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        raise Exception
