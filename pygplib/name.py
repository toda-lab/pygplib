"""Name manager class"""


class NameMgr:
    """Manages names of individual variables and constant symbols.

    The name of a variable symbol must begin with a lowercase letter,
    while the name of a constant symbol must begin with a uppercase letter.

    The name manager also manages names of propositional variables.

    Note:
        Names are added as soon as formulas are parsed,
        propositional variables are produced by perform_boolean_encoding().
        Also names can be added manually through lookup_index(),
        but in such a case, it is not checked whether it has a correct format.
        Actually, the name manager examines only the leading character,
        and it does not care of the second and later characters.
        See fo.py for the format of first-order formulas,
        and prop.py for that of propositional formulas.

    Attributes:
        _dict:  dict to find index from name.
        _inv_list:  list to find name from index.
    """

    _dict = {}
    _inv_list = []

    @classmethod
    def clear(cls) -> None:
        """Clears all names added so far."""
        cls._dict.clear()
        cls._inv_list.clear()

    @classmethod
    def lookup_index(cls, name: str) -> int:
        """Look-up index from name.

        Note:
            If not exists, a new index will be assigned.
            The method fails if names of auxiliary variables introduced by
            get_aux_index are given.
            If the leading character is "_" and the name is already registered,
            then this means that it is the index of an auxiliary variable.

        Args:
            name:   name of (variable or constant) symbol

        Raises:
            ValueError: if the leading character is not alphabetic.
        """
        if name[:1] == "_" and name in cls._dict:
            return cls._dict[name]
        if not name[:1].isalpha():
            raise ValueError("Leading character must be alphabetic.")
        if name not in cls._dict:
            cls._inv_list.append(name)
            cls._dict[name] = len(cls._inv_list)
        return cls._dict[name]


    @classmethod
    def get_aux_index(cls) -> int:
        """Gets the index of a new auxiliary variable to introduce.

        The leading character of variable name is "_" to avoid collision.
        """
        name = f"_{len(cls._inv_list)+1}"
        cls._inv_list.append(name)
        cls._dict[name] = len(cls._inv_list)
        return cls._dict[name]

    @classmethod
    def lookup_name(cls, index: int) -> str:
        """Look-up name from index.

        Raises:
            IndexError: if not exists.

        Args:
            index:  index of (variable or constant) symbol
        """
        if not 0 < index <= len(cls._inv_list):
            raise IndexError(f"No name is linked to {index}")
        return cls._inv_list[index - 1]

    @classmethod
    def has_index(cls, name: str) -> bool:
        """Does the name have index ?

        Args:
            name:   arbitrary string
        """
        return name in cls._dict

    @classmethod
    def has_name(cls, index: int) -> bool:
        """Does the index have name ?

        Args:
            index:   arbitrary integer
        """
        return 0 < index <= len(cls._inv_list)

    @classmethod
    def is_variable(cls, index: int) -> bool:
        """Is it a name for some variable ?

        Raises:
            ValueError: if the index does not have any name.

        Args:
            index:  index of (variable or constant) symbol
        """
        if not cls.has_name(index):
            raise ValueError(f"No name is linked to {index}")
        name = cls.lookup_name(index)
        return name[:1].islower() or name[:1] == "_"

    @classmethod
    def is_constant(cls, index: int) -> bool:
        """Is it a name for some constant ?

        Raises:
            ValueError: if the index does not have any name.

        Args:
            index:  index of (variable or constant) symbol
        """
        if not cls.has_name(index):
            raise ValueError(f"No name is linked to {index}")
        name = cls.lookup_name(index)
        return name[:1].isupper()
