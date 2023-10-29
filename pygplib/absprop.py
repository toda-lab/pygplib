"""Class of propositional logic with true and false and no variable"""

from .absexpr import AbsExpr
from .absexpr import IndexGen
from .absneg  import AbsNeg
from .baserelst import BaseRelSt


class AbsProp(AbsNeg):
    """Expression of Propositional Logic with true and false and no variable

    Attributes:
        _LAND:  string, representing logical conjunction.
        _LOR:   string, representing logical disjunction.
        _IMPLIES:   string, representing logical implication.
        _IFF:   string, representing logical equivalence.
        _ATOM_TAGS:  tuple of strings, representing types of atom.
        _BINOP_TAGS: tuple of strings, representing types of binary operator.
        _UNOP_TAGS: tuple of strings, representing types of uniary operator.
        _EXPR_TAGS: tuple of available tags in this class.
    """

    # Tag-related Variables and Methods
    _LAND = "&"
    _LOR = "|"
    _IMPLIES = "->"
    _IFF = "<->"

    _ATOM_TAGS = AbsNeg._ATOM_TAGS
    _BINOP_TAGS = (_LAND, _LOR, _IMPLIES, _IFF)
    _UNOP_TAGS = AbsNeg._UNOP_TAGS

    _EXPR_TAGS = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS

    @classmethod
    def get_land_tag(cls) -> str:
        """Gets tag of logical AND."""
        return cls._LAND

    @classmethod
    def get_lor_tag(cls) -> str:
        """Gets tag of logical OR."""
        return cls._LOR

    @classmethod
    def get_implies_tag(cls) -> str:
        """Gets tag of logical implication."""
        return cls._IMPLIES

    @classmethod
    def get_iff_tag(cls) -> str:
        """Gets tag of logical equivalence."""
        return cls._IFF

    # Constructor-related Methods
    @classmethod
    def land(cls, left: AbsExpr, right: AbsExpr) -> AbsExpr:
        """Gets the formula obtained by applying conjunction to operands.

        Args:
            left:   left operand
            right:  right operand
        """
        return cls(cls._LAND, left, right)

    @classmethod
    def lor(cls, left: AbsExpr, right: AbsExpr) -> AbsExpr:
        """Gets the formula obtained by applying disjunction to operands.

        Args:
            left:   left operand
            right:  right operand
        """
        return cls(cls._LOR, left, right)

    @classmethod
    def implies(cls, left: AbsExpr, right: AbsExpr) -> AbsExpr:
        """Gets the formula obtained by applying implication to operands.

        Args:
            left:   left operand
            right:  right operand
        """
        return cls(cls._IMPLIES, left, right)

    @classmethod
    def iff(cls, left: AbsExpr, right: AbsExpr) -> AbsExpr:
        """Gets the formula obtained by applying equivalence to operands.

        Args:
            left:   left operand
            right:  right operand
        """
        return cls(cls._IFF, left, right)

    @classmethod
    def binop(cls, tag: str, left: AbsExpr, right: AbsExpr) -> AbsExpr:
        """Gets the formula obtained applying the tag-specified operation.

        Args:
            tag:    tag of binary operation
            left:   left operand
            right:  right operand
        """
        if tag not in cls._BINOP_TAGS:
            raise ValueError(
                f"Expression tag, {tag}, is not available\
                in {cls.__name__}"
            )
        return cls(tag, left, right)

    @classmethod
    def binop_batch(cls, tag: str, expr_li: list) -> AbsExpr:
        """Gets the formula obtained from a list of formulas by recursively
        applying operation to the left and the right halves of the list.

        Args:
            tag:    tag of AND or OR operation
            expr_li:   list of operands
        """
        if len(expr_li) == 0:
            raise ValueError("Expression list is empty.")
        assert tag in [cls.get_land_tag(), cls.get_lor_tag()]

        def binop_batch_rec(tag: str, expr_li: list, begin: int, end: int) -> AbsExpr:
            assert begin < end

            if begin + 1 == end:
                return expr_li[begin]
            if begin + 2 == end:
                left = expr_li[begin]
                right = expr_li[begin + 1]
                return type(left).binop(tag, left, right)

            mid = (begin + end) // 2
            left = binop_batch_rec(tag, expr_li, begin, mid)
            right = binop_batch_rec(tag, expr_li, mid, end)
            return type(left).binop(tag, left, right)

        return binop_batch_rec(tag, expr_li, 0, len(expr_li))

    @classmethod
    def bitwise_binop(cls, tag: str, left_li: list, right_li: list) -> AbsExpr:
        """Performs binary operation in bitwise manner."""
        if len(left_li) != len(right_li):
            raise Exception("Unmatching list length")

        return [cls.binop(tag, le, ri) for le, ri in zip(left_li, right_li)]

    # Instance Methods
    def is_land_term(self) -> bool:
        """Is the top-most operator logical conjunction ?"""
        return self.get_tag() == type(self)._LAND

    def is_lor_term(self) -> bool:
        """Is the top-most operator logical disjunction ?"""
        return self.get_tag() == type(self)._LOR

    def is_implies_term(self) -> bool:
        """Is the top-most operator logical implication ?"""
        return self.get_tag() == type(self)._IMPLIES

    def is_iff_term(self) -> bool:
        """Is the top-most operator logical equivalence ?"""
        return self.get_tag() == type(self)._IFF

    def compute_nnf_step(self, negated: bool, s: list[list], t: list[list]) -> None:
        """Performs NNF computation for this object."""

        f = self.get_operand(1)
        g = self.get_operand(2)

        if self.is_land_term():
            if negated:
                # not (f and g) = not f or not g
                t.append([2, lambda y, z: type(self).lor(y, z)])
                s.append([True, f])
                s.append([True, g])
                return
            else:
                # f and g
                t.append([2, lambda y, z: type(self).land(y, z)])
                s.append([False, f])
                s.append([False, g])
                return

        if self.is_lor_term():
            if negated:
                # not (f or g) = not f and not g
                t.append([2, lambda y, z: type(self).land(y, z)])
                s.append([True, f])
                s.append([True, g])
                return
            else:
                # f or g
                t.append([2, lambda y, z: type(self).lor(y, z)])
                s.append([False, f])
                s.append([False, g])
                return

        if self.is_implies_term():
            if negated:
                # not (f -> g) = f and not g
                t.append([2, lambda y, z: type(self).land(y, z)])
                s.append([False, f])
                s.append([True, g])
                return
            else:
                # f -> g = not f or g
                t.append([2, lambda y, z: type(self).lor(y, z)])
                s.append([True, f])
                s.append([False, g])
                return

        if self.is_iff_term():
            if negated:
                # not (f <-> g) = not (f -> g) or not (g -> f)
                t.append([2, lambda y, z: type(self).lor(y, z)])
                s.append([True, type(self).implies(f, g)])
                s.append([True, type(self).implies(g, f)])
                return
            else:
                #    (f <-> g) =  (f -> g) and (g -> f)
                t.append([2, lambda y, z: type(self).land(y, z)])
                s.append([False, type(self).implies(f, g)])
                s.append([False, type(self).implies(g, f)])
                return

        super().compute_nnf_step(negated, s, t)

    def compute_cnf_step(self, igen: IndexGen, \
        assoc: dict, cnf: list) -> None:
        """Performs CNF computation for this object."""

        # a <-> b and c:  (-a or b) and (-a or c) and (a or -b or -c)
        if self.is_land_term():
            a = igen.get_next()
            b = assoc[id(self.get_operand(1))]
            c = assoc[id(self.get_operand(2))]

            cnf.append((-a, b))
            cnf.append((-a, c))
            cnf.append((a, -b, -c))

            assoc[id(self)] = a
            return

        # a <-> b or  c:  (a or -c) and (a or -b) and (-a or b or c)
        if self.is_lor_term():
            a = igen.get_next()
            b = assoc[id(self.get_operand(1))]
            c = assoc[id(self.get_operand(2))]

            cnf.append((a, -c))
            cnf.append((a, -b))
            cnf.append((-a, b, c))

            assoc[id(self)] = a
            return

        assert (
            not self.is_implies_term() and not self.is_iff_term()
        ), "compute_cnf_step() assumes reduced formulas"
        super().compute_cnf_step(igen, assoc, cnf)

    def reduce_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs reduce computation for this object."""
        if self.is_land_term():
            left = assoc[id(self.get_operand(1))]
            right = assoc[id(self.get_operand(2))]

            if left.is_true_atom():  # T and right = right
                assoc[id(self)] = right
                return

            if left.is_false_atom():  # F and right = F
                assoc[id(self)] = type(self).false_const()
                return

            if right.is_true_atom():  # left and T = left
                assoc[id(self)] = left
                return

            if right.is_false_atom():  # left and F = F
                assoc[id(self)] = type(self).false_const()
                return

            if left == right:  # left and left = left
                assoc[id(self)] = left
                return

            assoc[id(self)] = type(self).land(left, right)
            return

        if self.is_lor_term():
            left = assoc[id(self.get_operand(1))]
            right = assoc[id(self.get_operand(2))]

            if left.is_true_atom():  # T or right = T
                assoc[id(self)] = type(self).true_const()
                return

            if left.is_false_atom():  # F or right = right
                assoc[id(self)] = right
                return

            if right.is_true_atom():  # left or T = T
                assoc[id(self)] = type(self).true_const()
                return

            if right.is_false_atom():  # left or F = left
                assoc[id(self)] = left
                return

            if left == right:  # left or left = left
                assoc[id(self)] = left
                return

            assoc[id(self)] = type(self).lor(left, right)
            return

        super().reduce_step(assoc, st)

    def make_str_pre_step(self) -> str:
        """Makes string in prefix order for this object."""
        if (
            self.is_land_term()
            or self.is_lor_term()
            or self.is_implies_term()
            or self.is_iff_term()
        ):
            return "("
        return super().make_str_pre_step()

    def make_str_in_step(self) -> str:
        """Makes string in infix order for this object."""
        if self.is_land_term():
            return " " + type(self).get_land_tag() + " "
        if self.is_lor_term():
            return " " + type(self).get_lor_tag() + " "
        if self.is_implies_term():
            return " " + type(self).get_implies_tag() + " "
        if self.is_iff_term():
            return " " + type(self).get_iff_tag() + " "
        return super().make_str_in_step()

    def make_str_post_step(self) -> str:
        """Makes string in postfix order for this object."""
        if (
            self.is_land_term()
            or self.is_lor_term()
            or self.is_implies_term()
            or self.is_iff_term()
        ):
            return ")"
        return super().make_str_post_step()

    def make_node_str_step(self) -> str:
        """Makes string of this object for DOT print."""
        if self.is_land_term():
            return "AND"
        if self.is_lor_term():
            return "OR"
        if self.is_implies_term():
            return "IMP"
        if self.is_iff_term():
            return "IFF"
        return super().make_node_str_step()
