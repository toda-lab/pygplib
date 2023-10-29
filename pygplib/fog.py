"""Class of first-order logic of graphs"""

import functools

import pyparsing as pp
# Enables "packrat" parsing, which speedup parsing.
# See https://pyparsing-docs.readthedocs.io/en/latest/pyparsing.html .
pp.ParserElement.enable_packrat()

from .absexpr import AbsExpr
from .prop    import Prop
from .absfo   import AbsFo
from .name    import NameMgr
from .baserelst import BaseRelSt

class Fog(AbsFo):
    """Expression of First-order logic of graphs

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
        _EDG:   string, representing adjacency relation of vertices.
        _EQ:    string, representing equality relation of vertices.
        _ATOM_TAGS:  tuple of strings, representing types of atom.
        _BINOP_TAGS: tuple of strings, representing types of binary operator.
        _UNOP_TAGS: tuple of strings, representing types of uniary operator.
        _QF_TAGS:   tuple of strings, representing types of quantifier.
        _EXPR_TAGS: tuple of available tags in this class.
        _ATOM_BEGIN_POS: beginning position of the atom part of the aux field.
        _ATOM_LEN:  length of the atom part of the aux field.
        _AUX_LEN:   length of the aux field.
    """

    # Tag-related Variables and Methods
    _EDG = "edg"
    _EQ = "="

    _ATOM_TAGS = AbsFo._ATOM_TAGS + (_EDG, _EQ)
    _BINOP_TAGS = AbsFo._BINOP_TAGS
    _UNOP_TAGS = AbsFo._UNOP_TAGS
    _QF_TAGS = AbsFo._QF_TAGS

    _EXPR_TAGS = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS + _QF_TAGS

    _ATOM_BEGIN_POS = AbsFo._AUX_LEN
    _ATOM_LEN = 2
    _AUX_LEN = _ATOM_LEN + AbsFo._AUX_LEN

    @classmethod
    def get_edg_tag(cls) -> str:
        """Gets tag of edg."""
        return cls._EDG

    @classmethod
    def get_eq_tag(cls) -> str:
        """Gets tag of eq."""
        return cls._EQ

    # Constructor-related Methods
    @classmethod
    def _normalize_aux(cls, aux: tuple) -> tuple:
        """Normalize the order of arguments in relation symbol.

        The order is determined based on the order of names.
        """
        if aux == ():
            return (0,) * cls._AUX_LEN

        if (
            len(aux) == 3
            and aux[1] > 0
            and aux[2] > 0
            and NameMgr.lookup_name(aux[1]) > NameMgr.lookup_name(aux[2])
        ):
            return (aux[0], aux[2], aux[1])

        return aux

    @classmethod
    def edg(cls, x: int, y: int) -> AbsExpr:
        """Gets the atomic formula of the form edg(x,y).

        Args:
            x: index of (variable or constant) symbol
            y: index of (variable or constant) symbol
        """
        if not (NameMgr.has_name(x) and NameMgr.has_name(y)):
            raise ValueError("Specified index of edg has no name.")
        return cls(cls._EDG, aux=(0, x, y))

    @classmethod
    def eq(cls, x: int, y: int) -> AbsExpr:
        """Gets the atomic formula of the form x=y.

        Args:
            x: index of (variable or constant) symbol
            y: index of (variable or constant) symbol
        """
        if not (NameMgr.has_name(x) and NameMgr.has_name(y)):
            raise ValueError("Specified index of eq has no name.")
        return cls(cls._EQ, aux=(0, x, y))

    @classmethod
    def atom(cls, tag: str, x: int, y: int) -> AbsExpr:
        """Gets the tag-specified atomic formula.

        Args:
            x: index of (variable or constant) symbol (or 0 for true or false)
            y: index of (variable or constant) symbol (or 0 for true or false)
        """
        if tag not in cls._ATOM_TAGS:
            raise ValueError(
                f"Expression tag, {tag}, is not available in {cls.__name__}"
            )
        return cls(tag, aux=(0, x, y))

    # Instance Methods
    def get_atom_value(self, i: int) -> int:
        """Gets the term, specified by position, of the atomic formula.

        Args:
            i: position of term (1 or 2)
        """
        if not 0 < i <= type(self)._ATOM_LEN:
            raise IndexError(
                f"Value index should range from 1 to {type(self)._ATOM_LEN}"
            )
        return self._aux[type(self)._ATOM_BEGIN_POS + i - 1]

    def is_edg_atom(self) -> bool:
        """Is it an atom of the form edg(x,y) ?"""
        return self.get_tag() == type(self)._EDG

    def is_eq_atom(self) -> bool:
        """Is it an atom of the form x=y ?"""
        return self.get_tag() == type(self)._EQ

    def compute_nnf_step(self, negated: bool, s: list[list], t: list[list]) -> None:
        """Performs NNF computation for this object."""
        if self.is_edg_atom() or self.is_eq_atom():
            t.append([0, lambda: type(self).neg(self) if negated else self])
            return
        super().compute_nnf_step(negated, s, t)

    def substitute_step(self, y: int, x: int, assoc: dict) -> None:
        """Performs substitution for this object."""
        if self.is_edg_atom() or self.is_eq_atom():
            op = [self.get_atom_value(1), self.get_atom_value(2)]
            if op[0] == x:
                op[0] = y
            if op[1] == x:
                op[1] = y
            assoc[id(self)] = type(self).atom(self.get_tag(), op[0], op[1])
            return
        super().substitute_step(y, x, assoc)

    def get_free_vars_and_consts_pre_step(
        self, bound_vars: list, free_vars: list
    ) -> None:
        """Performs computatoin for this object."""
        if self.is_edg_atom() or self.is_eq_atom():
            v = self.get_atom_value(1)
            w = self.get_atom_value(2)

            if v not in bound_vars:
                free_vars.append(v)
            if w not in bound_vars:
                free_vars.append(w)
            return

        super().get_free_vars_and_consts_pre_step(bound_vars, free_vars)

    def reduce_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs reduce computatoin for this object."""

        if self.is_edg_atom():
            op = [self.get_atom_value(1), self.get_atom_value(2)]
            if op[0] == op[1]:  # always false regardless of graphs
                assoc[id(self)] = type(self).false_const()
                return
            if NameMgr.is_constant(op[0]) and NameMgr.is_constant(op[1]):
                if st != None:
                    if st.adjacent(op[0], op[1]):
                        assoc[id(self)] = type(self).true_const()
                    else:
                        assoc[id(self)] = type(self).false_const()
                    return
            assoc[id(self)] = self
            return

        if self.is_eq_atom():
            op = [self.get_atom_value(1), self.get_atom_value(2)]
            if op[0] == op[1]:  # always true regardless of graphs
                assoc[id(self)] = type(self).true_const()
                return
            if NameMgr.is_constant(op[0]) and NameMgr.is_constant(op[1]):
                if st != None:
                    if st.equal(op[0],op[1]):
                        assoc[id(self)] = type(self).true_const()
                    else:
                        assoc[id(self)] = type(self).false_const()
                    return
            assoc[id(self)] = self
            return

        super().reduce_step(assoc, st)

    def propnize_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs propositionalization for this object."""

        if self.is_edg_atom():
            atom = [self.get_atom_value(1), self.get_atom_value(2)]
            if atom[0] == atom[1]:
                assoc[id(self)] = st.encode_F()
            else:
                assoc[id(self)] = st.encode_edg(atom[0],atom[1])
            return

        if self.is_eq_atom():
            atom = [self.get_atom_value(1), self.get_atom_value(2)]
            if atom[0] == atom[1]: 
                assoc[id(self)] = st.encode_T()
            else:
                assoc[id(self)] = st.encode_eq(atom[0],atom[1])
            return

        if (\
            self.is_land_term()\
            or self.is_lor_term()\
            or self.is_implies_term()\
            or self.is_iff_term()\
        ):
            left  = assoc[id(self.get_operand(1))]
            right = assoc[id(self.get_operand(2))]
            assoc[id(self)] = Prop.binop(self.get_tag(), left, right)
            return

        if self.is_neg_term():
            op = assoc[id(self.get_operand(1))]
            assoc[id(self)] = Prop.neg(op)
            return

        if self.is_true_atom():
            assoc[id(self)] = st.encode_T()
            return

        if self.is_false_atom():
            assoc[id(self)] = st.encode_F()
            return

        assert False

    # Parser
    @classmethod
    def read(cls, formula_str: str) -> AbsExpr:
        """Constructs formula from string.

        The format of first-order formulas is defined here
        in Backus–Naur form. The following notation is useful shorthand.

        * e1 | e2 | e3 | ... means a choice of e1, e2, e3, etc.
        * ( e )* means zero or more occurences of e.
        * ["a"-"z"] matches any lowercase alphabet letter.
        * ["A"-"Z"] matches any uppercase alphabet letter.
        * ["0"-"9"] matches any digit from "0" to "9".
        * <word> means a non-terminal symbol.

        The name of a variable symbol is defined as follows::

            <var_symb>::= <alpha_lower> (<alpha_lower> | <digit> | "_")*
            <alpha_lower>::= ["a"-"z"]
            <digit>::= ["0"-"9"]

        The name of a constant symbol is defined as follows::

            <con_symb>::= <alpha_upper> (<alpha_upper> | <digit> | "_")*
            <alpha_upper>::= ["A"-"Z"]
            <digit>::= ["0"-"9"]

        An atomic formula is defined as follows::

            <atom>::= <edg_atom> | <eq_atom> | <con_atom>
            <edg_atom>::= "edg" "(" <term> "," <term> ")"
            <eq_atom>::=  <term> "=" <term>
            <con_atom>::= "T" | "F"
            <term>::= <var_symb> | <con_symb>

        A formula is defined as follows::

            <expr>::= <atom> | "(" <unop> <expr> ")"
                            | "(" <expr> <binop> <expr> ")"
                            | "(" <qf> "[" <var> "]" ":" <expr> ")"
            <unop>::= "~"
            <binop>::= "&" | "|" | "->" | "<->"
            <qf>::= "!" | "?"

        Parenthesis can be omitted as long as the interpretation is uniquely
        determined.
        Here, the precedence of logical operators is determined as follows::

            "!"="?" > "~" > "&" > "|" > "->" > "<->"

        Operators of the same precedence are associated in such a way
        that binary operations are left-associative, unary operation and
        quantifiers are right-associative.

        Note:
            ~ ! [x] : T means ~ (! [x] : T), but ! [x] : ~ T cannot be parsed 
            because the parser attempts to interprete it as (! [x] : ~) T 
            due to precedence, unless I misunderstand.

        Args:
            formula_str: string representation of formula
        """

        # The following tokens are suppressed in the parsed result.
        COMMA  = pp.Suppress(cls.get_comma_tag())
        LPAREN = pp.Suppress(cls.get_lparen_tag())
        RPAREN = pp.Suppress(cls.get_rparen_tag())

        # Variables are strings that match the pattern [a-z][a-z0-9_]* .
        # Constants are strings that match the pattern [A-Z][A-Z0-9_]* .
        VAR_SYMB = pp.Word(pp.srange("[a-z]"), pp.srange("[a-z0-9_]"))
        CON_SYMB = pp.Word(pp.srange("[A-Z]"), pp.srange("[A-Z0-9_]"))
        TERM = VAR_SYMB | CON_SYMB

        EDG_SYMB = pp.Literal(cls.get_edg_tag())
        EQ_SYMB = pp.Literal(cls.get_eq_tag())
        EDG_REL = EDG_SYMB + LPAREN + TERM + COMMA + TERM + RPAREN
        EQ_REL = TERM + EQ_SYMB + TERM

        TRUE = pp.Literal(cls.get_true_const_tag())
        FALSE = pp.Literal(cls.get_false_const_tag())
        CON_REL = TRUE | FALSE

        ATOM_EXPR = EDG_REL | EQ_REL | CON_REL

        UNOP = pp.Literal(cls.get_neg_tag())

        ANDOP = pp.Literal(cls.get_land_tag())
        OROP = pp.Literal(cls.get_lor_tag())
        IMPLIESOP = pp.Literal(cls.get_implies_tag())
        IFFOP = pp.Literal(cls.get_iff_tag())
        BINOP = pp.oneOf(" ".join(\
            [cls.get_land_tag(),cls.get_lor_tag(),\
            cls.get_implies_tag(),cls.get_iff_tag()]))

        ALLOP = pp.Literal(cls.get_forall_tag())
        EXISTSOP = pp.Literal(cls.get_exists_tag())
        QFOP = (ALLOP | EXISTSOP) \
                + pp.Suppress("[") \
                + VAR_SYMB + pp.Suppress("]") \
                + pp.Suppress(":")

        @VAR_SYMB.set_parse_action
        def action_var_symb(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            return NameMgr.lookup_index(tokens[0])

        @CON_SYMB.set_parse_action
        def action_con_symb(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            return NameMgr.lookup_index(tokens[0])

        @EDG_REL.set_parse_action
        def action_edg_rel(string, location, tokens):
            assert len(tokens) == 3, f"{tokens}"
            if tokens[0] == cls.get_edg_tag():
                op1 = int(tokens[1])
                op2 = int(tokens[2])
                return cls.edg(op1, op2)
            assert False

        @EQ_REL.set_parse_action
        def action_eq_rel(string, location, tokens):
            assert len(tokens) == 3, f"{tokens}"
            if tokens[1] == cls.get_eq_tag():
                op1 = int(tokens[0])
                op2 = int(tokens[2])
                return cls.eq(op1, op2)
            assert False

        @CON_REL.set_parse_action
        def action_con_rel(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            if tokens[0] == cls.get_false_const_tag():
                return cls.false_const()
            if tokens[0] == cls.get_true_const_tag():
                return cls.true_const()
            assert False

        def action_binop(string, location, tokens):
            # Accumulate tokens in left-associative way.
            # Many tokens may be given at once when the same operation appears.
            assert len(tokens) == 1, f"{tokens}"
            accum = tokens[0][0]
            for i in range(2, len(tokens[0]), 2):
                accum = cls.binop(tokens[0][i - 1], accum, tokens[0][i])
            return accum

        def action_unop(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            assert len(tokens[0]) == 2, f"{tokens[0]}"
            assert tokens[0][0] == cls.get_neg_tag(), f"{tokens[0]}"
            return cls.neg(tokens[0][1])

        def action_binop_batch(string, location, tokens):
            assert False not in [
                tokens[0][i] == tokens[0][1] for i in range(1, len(tokens[0]), 2)
            ]
            expr_li = [tokens[0][i] for i in range(0, len(tokens[0]), 2)]
            return cls.binop_batch(tokens[0][1], expr_li)

        def action_qfop(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            assert len(tokens[0]) == 3, f"{tokens[0]}"
            return cls.qf(tokens[0][0], tokens[0][2], tokens[0][1])

        # NOTE: Do not change the order of operators below,
        # which specifies the precedence of operators.
        #EXPR = pp.Forward()
        EXPR = pp.infix_notation(
            ATOM_EXPR,
            [
                (QFOP, 1, pp.opAssoc.RIGHT, action_qfop),
                (UNOP, 1, pp.opAssoc.RIGHT, action_unop),
                (
                    ANDOP,
                    2,
                    pp.opAssoc.LEFT,
                    action_binop_batch if cls.bipartite_order else action_binop,
                ),
                (
                    OROP,
                    2,
                    pp.opAssoc.LEFT,
                    action_binop_batch if cls.bipartite_order else action_binop,
                ),
                (IMPLIESOP, 2, pp.opAssoc.LEFT, action_binop),
                (IFFOP, 2, pp.opAssoc.LEFT, action_binop),
            ],
        )
        return EXPR.parse_string(formula_str, parse_all=True)[0]

    def make_str_pre_step(self) -> str:

        if self.is_edg_atom():
            name1 = NameMgr.lookup_name(self.get_atom_value(1))
            name2 = NameMgr.lookup_name(self.get_atom_value(2))
            return f"edg({name1}, {name2})"

        if self.is_eq_atom():
            name1 = NameMgr.lookup_name(self.get_atom_value(1))
            name2 = NameMgr.lookup_name(self.get_atom_value(2))
            return f"{name1} = {name2}"

        return super().make_str_pre_step()

    def make_str_in_step(self) -> str:

        if self.is_edg_atom():
            return ""

        if self.is_eq_atom():
            return ""

        return super().make_str_in_step()

    def make_str_post_step(self) -> str:

        if self.is_edg_atom():
            return ""

        if self.is_eq_atom():
            return ""

        return super().make_str_post_step()

    def make_node_str_step(self) -> str:

        if self.is_edg_atom() or self.is_eq_atom():

            op1 = (
                NameMgr.lookup_name(self.get_atom_value(1))
                if self.get_atom_value(1) != 0
                else "-"
            )
            op2 = (
                NameMgr.lookup_name(self.get_atom_value(2))
                if self.get_atom_value(2) != 0
                else "-"
            )

            return f'"edg({op1},{op2})"' if self.is_edg_atom() else f'"{op1}={op2}"'

        return super().make_node_str_step()
