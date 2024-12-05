"""Class of first-order logic of graphs"""

import warnings

from functools import cmp_to_key

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

    ::

        Node           |  self._aux[0]  | self._aux[1] 
        ---------------|----------------|--------------
        True  constant |  -             | -
        False constant |  -             | -
        Quantifier     | index of       | -
                       | bound variable |
        Relation       | 1st argument   | 2nd argument

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
        _LT:    string, representing less-than relation of vertices.
        _ATOM_TAGS:  tuple of strings, representing types of atom.
        _BINOP_TAGS: tuple of strings, representing types of binary operator.
        _UNOP_TAGS: tuple of strings, representing types of uniary operator.
        _QF_TAGS:   tuple of strings, representing types of quantifier.
        _EXPR_TAGS: tuple of available tags in this class.
    """

    # Tag-related Variables and Methods
    _EDG = "edg"
    _EQ = "="
    _LT = "<"

    _ATOM_TAGS = AbsFo._ATOM_TAGS + (_EDG, _EQ, _LT)
    _BINOP_TAGS = AbsFo._BINOP_TAGS
    _UNOP_TAGS = AbsFo._UNOP_TAGS
    _QF_TAGS = AbsFo._QF_TAGS

    _EXPR_TAGS = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS + _QF_TAGS

    @classmethod
    def get_edg_tag(cls) -> str:
        """Gets tag of edg."""
        return cls._EDG

    @classmethod
    def get_eq_tag(cls) -> str:
        """Gets tag of eq."""
        return cls._EQ

    @classmethod
    def get_lt_tag(cls) -> str:
        """Gets tag of lt."""
        return cls._LT

    
    @staticmethod
    def cmp_atom_args(x, y) -> int:
        if NameMgr.lookup_name(x) == NameMgr.lookup_name(y):
            return 0
        if NameMgr.lookup_name(x) < NameMgr.lookup_name(y):
            return -1
        if NameMgr.lookup_name(x) > NameMgr.lookup_name(y):
            return 1
        raise Exception()

    # Constructor-related Methods
    @classmethod
    def _normalize_aux(cls, tag: str, aux: tuple) -> tuple:
        """Normalize the order of arguments in relation symbol.

        The order is determined based on the order of names.
        """
        # sort aux if symmetric relation
        if tag in [cls.get_edg_tag(), cls.get_eq_tag()]:
            return tuple(sorted(aux, key=cmp_to_key(cls.cmp_atom_args)))
        # do not sort if non-symmetric relation
        if tag == cls.get_lt_tag():
            return aux
        assert len(aux) < 2
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
        return cls(cls._EDG, aux=(x, y))

    @classmethod
    def eq(cls, x: int, y: int) -> AbsExpr:
        """Gets the atomic formula of the form x=y.

        Args:
            x: index of (variable or constant) symbol
            y: index of (variable or constant) symbol
        """
        if not (NameMgr.has_name(x) and NameMgr.has_name(y)):
            raise ValueError("Specified index of eq has no name.")
        return cls(cls._EQ, aux=(x, y))

    @classmethod
    def lt(cls, x: int, y: int) -> AbsExpr:
        """Gets the atomic formula of the form lt(x,y).

        Args:
            x: index of (variable or constant) symbol
            y: index of (variable or constant) symbol
        """
        if not (NameMgr.has_name(x) and NameMgr.has_name(y)):
            raise ValueError("Specified index of lt has no name.")
        return cls(cls._LT, aux=(x,y))

    @classmethod
    def atom(cls, tag: str, *args) -> AbsExpr:
        """Gets the tag-specified atomic formula.

        Args:\
            args: tuple of indices of (variable or constant) symbols (or 0 for true or false)
        """
        if tag not in cls._ATOM_TAGS:
            raise ValueError(
                f"Expression tag, {tag}, is not available in {cls.__name__}"
            )
        assert len(args) == 2
        return cls(tag, aux=args)

    # Instance Methods
    def get_atom_value(self, i: int) -> int:
        """Gets the term, specified by position, of the atomic formula.

        Args:
            i: position of term (1 or 2)
        """
        warn_msg = "`get_atom_value()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.get_atom_arg(i)

    def get_atom_arg(self, i: int) -> int:
        """Gets the i-th argument of the atomic formula.

        Args:
            i: argument index (1 or 2)

        Returns:
            term given as argument of the atom.
        """
        if self.is_edg_atom() or self.is_eq_atom() or self.is_lt_atom():
            if i != 1 and i != 2:
                raise IndexError("Argument index should be 1 or 2")
        else:
            raise Exception("Unknown atom")
        return self._aux[i-1]

    def is_edg_atom(self) -> bool:
        """Is it an atom of the form edg(x,y) ?"""
        return self.get_tag() == type(self)._EDG

    def is_eq_atom(self) -> bool:
        """Is it an atom of the form x=y ?"""
        return self.get_tag() == type(self)._EQ

    def is_lt_atom(self) -> bool:
        """Is it an atom of the form x<y ?"""
        return self.get_tag() == type(self)._LT

    def compute_nnf_step(self, negated: bool, s: list[list], t: list[list]) -> None:
        """Performs NNF computation for this object."""
        if self.is_edg_atom() or self.is_eq_atom() or self.is_lt_atom():
            t.append([0, lambda: type(self).neg(self) if negated else self])
            return
        super().compute_nnf_step(negated, s, t)

    def substitute_step(self, y: int, x: int, assoc: dict) -> None:
        """Performs substitution for this object."""
        if self.is_edg_atom() or self.is_eq_atom() or self.is_lt_atom():
            op = [self.get_atom_arg(1), self.get_atom_arg(2)]
            for i, val in enumerate(op):
                if val == x:
                    op[i] = y
            assoc[id(self)] = type(self).atom(self.get_tag(), *op)
            return
        super().substitute_step(y, x, assoc)

    def get_free_vars_and_consts_pre_step(
        self, bound_vars: list, free_vars: list
    ) -> None:
        """Performs computation for this object."""
        if self.is_edg_atom() or self.is_eq_atom() or self.is_lt_atom():
            for v in self._aux:
                if v not in bound_vars:
                    free_vars.append(v)
            return

        super().get_free_vars_and_consts_pre_step(bound_vars, free_vars)

    def reduce_formula_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs reduce computation for this object."""

        if self.is_edg_atom():
            op = [self.get_atom_arg(1), self.get_atom_arg(2)]
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
            op = [self.get_atom_arg(1), self.get_atom_arg(2)]
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

        if self.is_lt_atom():
            op = [self.get_atom_arg(1), self.get_atom_arg(2)]
            if op[0] == op[1]:
                assoc[id(self)] = type(self).false_const()
                return
            if NameMgr.is_constant(op[0]) and NameMgr.is_constant(op[1]):
                if st != None:
                    if st.lt(op[0], op[1]):
                        assoc[id(self)] = type(self).true_const()
                    else:
                        assoc[id(self)] = type(self).false_const()
                    return
            assoc[id(self)] = self
            return

        super().reduce_formula_step(assoc, st)

    def perform_boolean_encoding_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs Boolean encoding for this object."""
        if self.is_edg_atom():
            atom = [self.get_atom_arg(1), self.get_atom_arg(2)]
            if atom[0] == atom[1]:
                assoc[id(self)] = st.be_F()
            else:
                assoc[id(self)] = st.be_edg(atom[0],atom[1])
            return

        if self.is_eq_atom():
            atom = [self.get_atom_arg(1), self.get_atom_arg(2)]
            if atom[0] == atom[1]: 
                assoc[id(self)] = st.be_T()
            else:
                assoc[id(self)] = st.be_eq(atom[0],atom[1])
            return

        if self.is_lt_atom():
            atom = [self.get_atom_arg(1), self.get_atom_arg(2)]
            if atom[0] == atom[1]:
                assoc[id(self)] = st.be_F()
            else:
                assoc[id(self)] = st.be_lt(atom[0],atom[1])
            return

        if (\
            self.is_land()\
            or self.is_lor()\
            or self.is_implies()\
            or self.is_iff()\
        ):
            left  = assoc[id(self.get_operand(1))]
            right = assoc[id(self.get_operand(2))]
            assoc[id(self)] = Prop.binop(self.get_tag(), left, right)
            return

        if self.is_neg():
            op = assoc[id(self.get_operand(1))]
            assoc[id(self)] = Prop.neg(op)
            return

        if self.is_true_atom():
            assoc[id(self)] = st.be_T()
            return

        if self.is_false_atom():
            assoc[id(self)] = st.be_F()
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

            <atom>::= <edg_atom> | <eq_atom> | <con_atom> | <lt_atom>
            <edg_atom>::= "edg" "(" <term> "," <term> ")"
            <eq_atom>::=  <term> "=" <term>
            <con_atom>::= "T" | "F"
            <lt_atom>::=  <term> "<" <term>
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
        if formula_str.strip() == "":
            raise Exception("no formula given")

        # The following tokens are suppressed in the parsed result.
        COMMA  = pp.Suppress(cls.get_comma_tag())
        LPAREN = pp.Suppress(cls.get_lparen_tag())
        RPAREN = pp.Suppress(cls.get_rparen_tag())

        # Variables are strings that match the pattern [a-z_][a-z0-9_]* .
        # Constants are strings that match the pattern [A-Z][A-Z0-9_]* .
        VAR_SYMB = pp.Word(pp.srange("[a-z]"), pp.srange("[a-z0-9_]"))
        CON_SYMB = pp.Word(pp.srange("[A-Z]"), pp.srange("[A-Z0-9_]"))
        TERM = VAR_SYMB | CON_SYMB

        EDG_SYMB = pp.Literal(cls.get_edg_tag())
        EQ_SYMB  = pp.Literal(cls.get_eq_tag())
        LT_SYMB  = pp.Literal(cls.get_lt_tag())
        EDG_REL = EDG_SYMB + LPAREN + TERM + COMMA + TERM + RPAREN
        EQ_REL  = TERM + EQ_SYMB + TERM
        LT_REL  = TERM + LT_SYMB + TERM

        TRUE  = pp.Literal(cls.get_true_const_tag())
        FALSE = pp.Literal(cls.get_false_const_tag())
        CON_REL = TRUE | FALSE

        ATOM_EXPR = EDG_REL | LT_REL | EQ_REL | CON_REL

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

        @LT_REL.set_parse_action
        def action_lt_rel(string, location, tokens):
            assert len(tokens) == 3, f"{tokens}"
            if tokens[1] == cls.get_lt_tag():
                op1 = int(tokens[0])
                op2 = int(tokens[2])
                return cls.lt(op1, op2)
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
                    action_binop_batch,
                ),
                (
                    OROP,
                    2,
                    pp.opAssoc.LEFT,
                    action_binop_batch,
                ),
                (IMPLIESOP, 2, pp.opAssoc.LEFT, action_binop),
                (IFFOP, 2, pp.opAssoc.LEFT, action_binop),
            ],
        )
        return EXPR.parse_string(formula_str, parse_all=True)[0]

    def make_str_pre_step(self) -> str:

        if self.is_edg_atom():
            name1 = NameMgr.lookup_name(self.get_atom_arg(1))
            name2 = NameMgr.lookup_name(self.get_atom_arg(2))
            return f"edg({name1}, {name2})"

        if self.is_eq_atom():
            name1 = NameMgr.lookup_name(self.get_atom_arg(1))
            name2 = NameMgr.lookup_name(self.get_atom_arg(2))
            return f"{name1} = {name2}"

        if self.is_lt_atom():
            name1 = NameMgr.lookup_name(self.get_atom_arg(1))
            name2 = NameMgr.lookup_name(self.get_atom_arg(2))
            return f"{name1} < {name2}"

        return super().make_str_pre_step()

    def make_str_in_step(self) -> str:

        if self.is_edg_atom():
            return ""

        if self.is_eq_atom():
            return ""

        if self.is_lt_atom():
            return ""

        return super().make_str_in_step()

    def make_str_post_step(self) -> str:

        if self.is_edg_atom():
            return ""

        if self.is_eq_atom():
            return ""

        if self.is_lt_atom():
            return ""

        return super().make_str_post_step()

    def make_node_str_step(self) -> str:

        if self.is_edg_atom() or self.is_eq_atom() or self.is_lt_atom():
            op = []
            for val in self._aux:
                op.append(NameMgr.lookup_name(val) if val != 0 else "-")
            if self.is_edg_atom():
                return f'"edg({op[0]},{op[1]})"'
            if self.is_eq_atom():
                return f'"{op[0]}={op[1]}"'
            if self.is_edg_atom():
                return f'"{op[0]}<{op[1]}"'
        return super().make_node_str_step()
