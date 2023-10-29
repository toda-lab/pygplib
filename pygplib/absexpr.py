"""Base class of logical formula as well as index generator"""

from .baserelst import BaseRelSt

class IndexGen:
    """Generates indices.

    Args:
        init_index: initial index

    Attributes:
        _init: initial index
        _next: next index
    """

    def __init__(self, init_index: int = 1):
        """Initializes index with init_index."""
        self._init = init_index
        self._next = init_index

    def get_next(self) -> int:
        """Gets the next index."""
        res = self._next
        self._next += 1
        return res

    def get_count(self) -> int:
        """Gets the number of indices issued so far."""
        return self._next - self._init

    def clear(self, init_index: int = 1) -> None:
        """Clears index with init_index."""
        self._next = init_index


class AbsExpr:
    """Abstract class of logical formulas.

    Each formula is a graph made up of objects of the same formula class.
    Each such object represents either an atom or a logical operator with
    operands.
    Instance methods are operations related to a single object
    such as getters of object fields, while class methods are
    operations for the whole formula.
    Each formula class is supposed to have dedicated constructor,
    and it is not supposed to create a new object
    by invoking an ordinary constructor directly like AbsExpr().

    Attributes:
        _unique_table: dict. to find an object from its string representation.
        _ATOM_TAGS:  tuple of strings, representing types of atom.
        _BINOP_TAGS: tuple of strings, representing types of binary operator.
        _UNOP_TAGS: tuple of strings, representing types of uniary operator.
        _EXPR_TAGS: tuple of available tags in this class.
        _COMMA: string to represent comma.
        _LPAREN:    string to represent left parentheses.
        _RPAREN:    string to represent right parentheses.
        _ATOM_LEN:  length of atom part in aux field.
        _AUX_LEN:   length of aux field.

    Note:
        The current implementation, for the sake of simplicity,
        does not provide the functionality of deleting unnecessary objects.
    """

    _unique_table = {}
    bipartite_order = False
    """enables bipartite order of applying operations"""

    # Tag-related Variables and Methods
    _ATOM_TAGS = ()
    _BINOP_TAGS = ()
    _UNOP_TAGS = ()

    _EXPR_TAGS = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS

    _COMMA = ","
    _LPAREN = "("
    _RPAREN = ")"

    _ATOM_LEN = 0
    _AUX_LEN = _ATOM_LEN

    @classmethod
    def get_lparen_tag(cls) -> str:
        """Gets tag of left parenthesis."""
        return cls._LPAREN

    @classmethod
    def get_rparen_tag(cls) -> str:
        """Gets tag of right parenthesis."""
        return cls._RPAREN

    @classmethod
    def get_comma_tag(cls) -> str:
        """Gets tag of comma."""
        return cls._COMMA

    # Constructor-related Methods
    @staticmethod
    def _to_key(tag: str, left: "AbsExpr", right: "AbsExpr", aux: tuple) -> str:
        """Makes key to identify expression."""
        tup = (tag, id(left), id(right)) + aux
        return ",".join(map(str, tup))

    @classmethod
    def _normalize_aux(cls, aux: tuple) -> tuple:
        """This method might be overridden to normalize atom operands' order"""
        return (0,) * cls._AUX_LEN if aux == () else aux

    def __new__(
        cls, tag: str, left: "AbsExpr" = None, right: "AbsExpr" = None, aux: tuple = ()
    ):
        """Creates a new object only if no identical formula exists.

        Each formula class will provide dedicated constructors, and
        it is not supposed to create an object by involing like AbsExpr().

        Args:
            tag:    string representing the top-most operator
            left:   left operand
            right:  right operand
            aux:    information regarding bound variable and atom
        """
        aux = cls._normalize_aux(aux)
        key = cls._to_key(tag, left, right, aux)

        if key in cls._unique_table:
            return cls._unique_table[key]

        new = super().__new__(cls)
        cls._unique_table[key] = new

        # NOTE: A new object is initialized here.
        new._tag = tag
        new._left = left
        new._right = right
        new._aux = aux
        return new

    # Instance Methods
    def get_tag(self) -> str:
        """Gets the tag of the top-most operator of the formula."""
        return self._tag

    def get_operand(self, i: int) -> "AbsExpr":
        """Gets an operand of the top-most operator of the formula.

        For binary operation, the left operand and the right operand
        are returned when i = 1 and 2, respectively.
        For quanfier and unary operation, the unique operand is
        returned when i = 1.
        """
        if i not in (1, 2):
            raise IndexError("Index of operand should be either 1 or 2")
        return self._left if i == 1 else self._right

    def is_atom_term(self) -> bool:
        """Is it an atomic formula ?"""
        return self.get_tag() in type(self)._ATOM_TAGS

    def is_unop_term(self) -> bool:
        """Is the top-most operator a unary operation ?"""
        return self.get_tag() in type(self)._UNOP_TAGS

    def is_binop_term(self) -> bool:
        """Is the top-most operator a binary operation ?"""
        return self.get_tag() in type(self)._BINOP_TAGS

    def gen_key(self) -> str:
        """Converts object into string.

        The returned string consists of the top-most operator and its operands
        only, which is mainly used as identifiers
        (as keys for _unique_table) to decide whether formulas
        are syntatically identical.
        """
        return type(self)._to_key(self._tag, self._left, self._right, self._aux)

    def compute_nnf_step(self, negated: bool, s: list[list], t: list[list]) -> None:
        """Performs NNF compuation for this object."""
        assert False, f"{self.gen_key()}"

    def compute_cnf_step(self, igen: IndexGen, \
        assoc: dict, cnf: list) -> None:
        """Performs CNF compuation for this object."""
        assert False, f"{self.gen_key()}"

    def reduce_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs reduce compuation for this object."""
        assert False, f"{self.gen_key()}"

    def make_str_pre_step(self) -> str:
        """Makes string of this object in prefix order."""
        assert False, f"{self.gen_key()}"

    def make_str_in_step(self) -> str:
        """Makes string of this object in infix order."""
        assert False, f"{self.gen_key()}"

    def make_str_post_step(self) -> str:
        """Makes string of this object in postfix order."""
        assert False, f"{self.gen_key()}"

    def make_node_str_step(self) -> str:
        """Makes string of this object for DOT print."""
        assert False, f"{self.gen_key()}"
