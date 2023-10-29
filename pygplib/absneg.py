"""Class of abstract logical formula with true/false constants and negation"""
from .absexpr import AbsExpr
from .absexpr import IndexGen
from .baserelst import BaseRelSt


class AbsNeg(AbsExpr):
    """Class of abstract expressions with true and false and negation only.

    Attributes:
        _NEG:   string, representing logical negation.
        _TRUE_CONST:    string, representing true.
        _FALSE_CONST:   string, representing false.
        _ATOM_TAGS:  tuple of strings, representing types of atom.
        _BINOP_TAGS: tuple of strings, representing types of binary operator.
        _UNOP_TAGS: tuple of strings, representing types of uniary operator.
        _EXPR_TAGS: tuple of available tags in this class.
    """

    # Tag-related Variables and Methods
    _NEG = "~"
    _TRUE_CONST = "T"
    _FALSE_CONST = "F"

    _ATOM_TAGS = AbsExpr._ATOM_TAGS + (_TRUE_CONST, _FALSE_CONST)
    _BINOP_TAGS = AbsExpr._BINOP_TAGS
    _UNOP_TAGS = (_NEG,)

    _EXPR_TAGS = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS

    @classmethod
    def get_neg_tag(cls) -> str:
        """Gets tag of negation."""
        return cls._NEG

    @classmethod
    def get_true_const_tag(cls) -> str:
        """Gets tag of true constant."""
        return cls._TRUE_CONST

    @classmethod
    def get_false_const_tag(cls) -> str:
        """Gets tag of false constant."""
        return cls._FALSE_CONST

    # Constructor-related Methods
    @classmethod
    def neg(cls, left: AbsExpr) -> AbsExpr:
        """Gets the formula obtained by applying negation to the operand.

        Args:
            left:   the formula to be negated
        """
        return cls(cls._NEG, left)

    @classmethod
    def true_const(cls) -> AbsExpr:
        """Gets the true atom, the atom that always evaluates to true."""
        return cls(cls._TRUE_CONST)

    @classmethod
    def false_const(cls) -> AbsExpr:
        """Gets the false atom, the atom that always evaluates to false."""
        return cls(cls._FALSE_CONST)

    # Instance Methods
    def is_neg_term(self) -> bool:
        """Is the top-most operator the logical negation ?"""
        return self.get_tag() == type(self)._NEG

    def is_true_atom(self) -> bool:
        """Is it the true atom ?"""
        return self.get_tag() == type(self)._TRUE_CONST

    def is_false_atom(self) -> bool:
        """Is it the false atom ?"""
        return self.get_tag() == type(self)._FALSE_CONST

    def is_const_atom(self) -> bool:
        """Is it either the true atom or the false atom ?"""
        return self.is_true_atom() or self.is_false_atom()

    def compute_nnf_step(self, negated: bool, s: list[list], t: list[list]) -> None:
        """Perform NNF computation for this object."""

        if self.is_neg_term():  # not not f = f
            f = self.get_operand(1)
            s.append([not negated, f])
            t.append([1, lambda x: x])
            return

        if self.is_true_atom() or self.is_false_atom():
            if negated:
                t.append([0, lambda: type(self).neg(self)])
            else:
                t.append([0, lambda: self])
            return

        super().compute_nnf_step(negated, s, t)

    def compute_cnf_step(self, igen: IndexGen, \
        assoc: dict, cnf: list) -> None:
        """Performs CNF computation for this object."""
        if self.is_neg_term():  # a <-> -b :  (-a or -b) and (a or b)
            a = igen.get_next()
            b = assoc[id(self.get_operand(1))]

            cnf.append((-a, -b))
            cnf.append((a, b))

            assoc[id(self)] = a
            return

        assert (
            not self.is_true_atom() and not self.is_false_atom()
        ), "compute_cnf_step() assumes reduced formulas"
        super().compute_cnf_step(igen, assoc, cnf)

    def reduce_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs reduce computation for this object."""
        if self.is_neg_term():
            g = assoc[id(self.get_operand(1))]
            if g.is_true_atom():
                assoc[id(self)] = type(self).false_const()
                return
            if g.is_false_atom():
                assoc[id(self)] = type(self).true_const()
                return
            assoc[id(self)] = type(self).neg(g)
            return
        if self.is_true_atom() or self.is_false_atom():
            assoc[id(self)] = self
            return
        super().reduce_step(assoc, st)

    def make_str_pre_step(self) -> str:
        """Makes string in prefix order for this object."""
        if self.is_neg_term():
            out = "(" + type(self).get_neg_tag() + " "
            return out
        if self.is_true_atom():
            return type(self).get_true_const_tag()
        if self.is_false_atom():
            return type(self).get_false_const_tag()
        return super().make_str_pre_step()

    def make_str_in_step(self) -> str:
        """Makes string in infix order for this object."""
        if self.is_neg_term():
            return ""
        if self.is_true_atom():
            return ""
        if self.is_false_atom():
            return ""
        return super().make_str_in_step()

    def make_str_post_step(self) -> str:
        """Makes string in postfix order for this object."""
        if self.is_neg_term():
            return ")"
        if self.is_true_atom():
            return ""
        if self.is_false_atom():
            return ""
        return super().make_str_post_step()

    def make_node_str_step(self) -> str:
        """Makes string of this object for DOT print."""
        if self.is_neg_term():
            return "NOT"
        if self.is_true_atom():
            return "T"
        if self.is_false_atom():
            return "F"
        return super().make_node_str_step()
