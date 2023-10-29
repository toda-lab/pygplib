"""Class of first-order logic of graphs with True, False, and no other atom"""

from .absexpr import AbsExpr
from .absprop import AbsProp
from .name    import NameMgr
from .baserelst import BaseRelSt


class AbsFo(AbsProp):
    """First-order logic of graphs with true and false and no other atoms.

    Note:
        In the current implementation, syntactically identical subexpressions
        are shared. We have to keep it in mind that this might become source of
        bugs.
        For instance, consider (? [x] : x) & x.
        In this formula, the second occurrence of x is a bound variable, and
        third occurrence is a free variable.
        In the current implementation, despite different semantics,
        these variables are shared, that is, they are represented as a single
        object in the representation of the formula.
        We do this for the sake of simplicity, but this might become source of
        bugs. When we apply some operation to such a formula, we sometimes
        have to consider difference in semantics.

    Attributes:
        _FORALL:   string, representing universal quantifier.
        _EXISTS:   string, representing existential quantifier.
        _ATOM_TAGS:  tuple of strings, representing types of atom.
        _BINOP_TAGS: tuple of strings, representing types of binary operator.
        _UNOP_TAGS: tuple of strings, representing types of uniary operator.
        _QF_TAGS:   tuple of strings, representing types of quantifier.
        _EXPR_TAGS: tuple of available tags in this class.
        _BOUND_VAR_POS: beginning position of the field of bound variable.
        _AUX_LEN:   length of aux field.
    """

    # Tag-related Variables and Methods
    _FORALL = "!"
    _EXISTS = "?"

    _ATOM_TAGS = AbsProp._ATOM_TAGS
    _BINOP_TAGS = AbsProp._BINOP_TAGS
    _UNOP_TAGS = AbsProp._UNOP_TAGS
    _QF_TAGS = (_FORALL, _EXISTS)

    _EXPR_TAGS = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS + _QF_TAGS

    _BOUND_VAR_POS = AbsProp._AUX_LEN
    _AUX_LEN = 1 + AbsProp._AUX_LEN

    @classmethod
    def get_forall_tag(cls) -> str:
        """Gets tag of forall."""
        return cls._FORALL

    @classmethod
    def get_exists_tag(cls) -> str:
        """ "Gets tag of exists."""
        return cls._EXISTS

    # Constructor-related Methods
    @classmethod
    def forall(cls, left: AbsExpr, bvar: int) -> AbsExpr:
        """Gets the formula obtained by applying universal quantifier.

        Args:
            left:   formula to be quantified
            bvar:    index of variable to be bounded.
        """
        if not NameMgr.is_variable(bvar):
            raise ValueError(f"{NameMgr.lookup_name(bvar)} is not a variable symbol.")
        return cls(cls._FORALL, left, aux=(bvar,))

    @classmethod
    def exists(cls, left: AbsExpr, bvar: int) -> AbsExpr:
        """Gets the formula obtained by applying existential quantifier.

        Args:
            left:   formula to be quantified
            bvar:    index of variable to be bounded.
        """
        if not NameMgr.is_variable(bvar):
            raise ValueError(f"{NameMgr.lookup_name(bvar)} is not a variable symbol.")
        return cls(cls._EXISTS, left, aux=(bvar,))

    @classmethod
    def qf(cls, tag: str, left: AbsExpr, bvar: int) -> AbsExpr:
        """Gets the formula obtained by applying the tag-specified quantifier.

        Args:
            tag:    tag of quantifier
            left:   formula to be quantified
            bvar:    index of variable to be bounded.
        """
        if tag not in cls._QF_TAGS:
            raise ValueError(
                f"Expression tag, {tag}, is not available in {cls.__name__}"
            )
        return cls(tag, left, aux=(bvar,))

    # Instance Methods
    def get_bound_var(self) -> int:
        """Gets the index of bound variable."""
        if not self.is_qf_term():
            raise Exception("The top-most operator of the formula is not quantifier.")
        return self._aux[type(self)._BOUND_VAR_POS]

    def is_forall_term(self) -> bool:
        """Is the top-most operator the universal quantifier ?"""
        return self.get_tag() == type(self)._FORALL

    def is_exists_term(self) -> bool:
        """Is the top-most operator the existential quantifier ?"""
        return self.get_tag() == type(self)._EXISTS

    def is_qf_term(self) -> bool:
        """Is the top-most operator universal or existential quantifier ?"""
        return self.get_tag() in type(self)._QF_TAGS

    def compute_nnf_step(self, negated: bool, s: list[list], t: list[list]) -> None:
        """Performs NNF computation for this object."""

        f = self.get_operand(1)

        if self.is_forall_term():  # not ! f = ? not f
            bvar = self.get_bound_var()
            t.append(
                [
                    1,
                    lambda z: type(self).exists(z, bvar)
                    if negated
                    else type(self).forall(z, bvar),
                ]
            )
            s.append([negated, f])
            return

        if self.is_exists_term():  # not ? f = ! not f
            bvar = self.get_bound_var()
            t.append(
                [
                    1,
                    lambda z: type(self).forall(z, bvar)
                    if negated
                    else type(self).exists(z, bvar),
                ]
            )
            s.append([negated, f])
            return

        super().compute_nnf_step(negated, s, t)

    def get_free_vars_and_consts_pre_step(
        self, bound_vars: list, free_vars: list
    ) -> None:
        """Performs computation in prefix order for this object."""
        if self.is_forall_term() or self.is_exists_term():
            bound_vars.append(self.get_bound_var())
            return

    def get_free_vars_and_consts_post_step(
        self, bound_vars: list, free_vars: list
    ) -> None:
        """Performs computation in postfix order for this object."""
        if self.is_forall_term() or self.is_exists_term():
            bound_vars.remove(self.get_bound_var())
            return

    def substitute_step(self, y: int, x: int, assoc: dict) -> None:
        """Performs substitution for this object."""

        if self.is_neg_term():
            g = assoc[id(self.get_operand(1))]
            assoc[id(self)] = type(self).neg(g)
            return

        if self.is_true_atom() or self.is_false_atom():
            assoc[id(self)] = self
            return

        if (
            self.is_land_term()
            or self.is_lor_term()
            or self.is_implies_term()
            or self.is_iff_term()
        ):
            left = assoc[id(self.get_operand(1))]
            right = assoc[id(self.get_operand(2))]
            assoc[id(self)] = type(self).binop(self.get_tag(), left, right)
            return

        if self.is_forall_term() or self.is_exists_term():
            bvar = self.get_bound_var()
            if bvar == x:
                assoc[id(self)] = self
            else:
                g = assoc[id(self.get_operand(1))]
                assoc[id(self)] = type(self).qf(self.get_tag(), g, bvar)
            return

        assert False

    def reduce_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs reduce compuation for this object."""

        if self.is_forall_term():
            bvar = self.get_bound_var()
            g = assoc[id(self.get_operand(1))]

            if g.is_true_atom():
                # ! [x] : T = T
                assoc[id(self)] = type(self).true_const()
                return

            if g.is_false_atom():
                if st != None:
                    if len(st.domain) > 0:
                        # ! [x] : F = F if there is at least one object.
                        assoc[id(self)] = type(self).false_const()
                    else:
                        # ! [x] : F = T if there is no object.
                        assoc[id(self)] = type(self).true_const()
                    return

            assoc[id(self)] = type(self).forall(g, bvar)
            return

        if self.is_exists_term():
            bvar = self.get_bound_var()
            g = assoc[id(self.get_operand(1))]

            if g.is_true_atom():
                if st != None:
                    if len(st.domain) > 0:
                        # ? [x] : T = T if there is at least one object.
                        assoc[id(self)] = type(self).true_const()
                    else:
                        # ? [x] : T = F if there is no object.
                        assoc[id(self)] = type(self).false_const()
                    return

            if g.is_false_atom():
                # ? [x] : F = F
                assoc[id(self)] = type(self).false_const()
                return

            assoc[id(self)] = type(self).exists(g, bvar)
            return

        super().reduce_step(assoc, st)

    def make_str_pre_step(self) -> str:
        """Makes string in prefix order for this object."""
        if self.is_forall_term() or self.is_exists_term():
            out = "("
            out += ( \
                type(self).get_forall_tag() if self.is_forall_term() \
                                       else type(self).get_exists_tag()\
            )
            out += " "
            out += f"[{NameMgr.lookup_name(self.get_bound_var())}] :"
            out += " "
            return out
        return super().make_str_pre_step()

    def make_str_in_step(self) -> str:
        """Makes string in infix order for this object."""
        if self.is_forall_term() or self.is_exists_term():
            return ""
        return super().make_str_in_step()

    def make_str_post_step(self) -> str:
        """Makes string in postfix order for this object."""
        if self.is_forall_term() or self.is_exists_term():
            return ")"
        return super().make_str_post_step()

    def make_node_str_step(self) -> str:
        """Makes string of this object for DOT print."""
        if self.is_forall_term() or self.is_exists_term():
            bvar = self.get_bound_var()
            name = NameMgr.lookup_name(bvar)
            return f'"! [{name}] :"' if self.is_forall_term() else f'"? [{name}] :"'
        return super().make_node_str_step()
