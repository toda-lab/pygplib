"""Class of propositional logic"""

import pyparsing as pp
# Enables "packrat" parsing, which speedup parsing.
# See https://pyparsing-docs.readthedocs.io/en/latest/pyparsing.html .
pp.ParserElement.enable_packrat()

from .absexpr import AbsExpr
from .absexpr import IndexGen
from .absprop import AbsProp
from .name import NameMgr
from .baserelst import BaseRelSt


class Prop(AbsProp):
    """Expression of Propositional Logic

    Attributes:
        _VAR:   string, representing Boolean variable.
        _ATOM_TAGS:  tuple of strings, representing types of atom.
        _BINOP_TAGS: tuple of strings, representing types of binary operator.
        _UNOP_TAGS: tuple of strings, representing types of uniary operator.
        _EXPR_TAGS: tuple of available tags in this class.
        _ATOM_BEGIN_POS: beginning position of the atom part of the aux field.
        _ATOM_LEN:  length of the atom part of the aux field.
        _AUX_LEN:   length of the aux field.
    """

    # Tag-related Variables and Methods
    _VAR = "X"

    _ATOM_TAGS = AbsProp._ATOM_TAGS + (_VAR,)
    _BINOP_TAGS = AbsProp._BINOP_TAGS
    _UNOP_TAGS = AbsProp._UNOP_TAGS

    _EXPR_TAGS = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS

    _ATOM_BEGIN_POS = AbsProp._AUX_LEN
    _ATOM_LEN = 1
    _AUX_LEN = _ATOM_LEN + AbsProp._AUX_LEN

    @classmethod
    def get_var_tag(cls):
        """Gets tag of var."""
        return cls._VAR

    # Constructor-related Methods
    @classmethod
    def var(cls, index: int):
        """Gets the formula of the index-speficied Boolean variable."""
        if not NameMgr.has_name(index):
            raise ValueError(f"Index {index} is no name")
        return cls(cls._VAR, aux=(index,))

    # Instance Methods
    def get_atom_value(self, i: int) -> int:
        """Gets the index of the Boolean variable."""
        if not self.is_var_atom():
            raise Exception("The formula is not a Boolean variable.")
        if not 0 < i <= type(self)._ATOM_LEN:
            raise IndexError(
                "Value index \
                should range 1 to type(self)._ATOM_LEN"
            )
        return self._aux[type(self)._ATOM_BEGIN_POS + i - 1]

    def get_var_index(self):
        """Gets the index of the Boolean variable."""
        return self.get_atom_value(1)

    def is_var_atom(self):
        """Is the formula a Boolean variable ?"""
        return self.get_tag() == type(self)._VAR

    def compute_nnf_step(self, negated: bool, s: list[list], t: list[list]) -> None:
        """Performs NNF computation for this object."""
        if self.is_var_atom():
            t.append([0, lambda: type(self).neg(self) if negated else self])
            return
        super().compute_nnf_step(negated, s, t)

    def compute_cnf_step(self, igen: IndexGen, \
        assoc: dict, cnf: list) -> None:
        """Peforms CNF computation for this object."""
        if self.is_var_atom():
            assoc[id(self)] = self.get_var_index()
        else:
            super().compute_cnf_step(igen, assoc, cnf)

    # Parser
    @classmethod
    def read(cls, formula_str: str) -> AbsExpr:
        """Constructs formula from string.

        The format of propositional formulas is defined here
        in Backus–Naur form. The following notation is useful shorthand.

        * e1 | e2 | e3 | ... means a choice of e1, e2, e3, etc.
        * ( e )* means zero or more occurences of e.
        * ( e )+ means one or more occurences of e.
        * ["a"-"z"] matches any lowercase alphabet letter.
        * ["A"-"Z"] matches any uppercase alphabet letter.
        * ["0"-"9"] matches any digit from "0" to "9".
        * <word> means a non-terminal symbol.

        The name of a variable symbol is defined as follows::

            <var_symb>::= <alpha_lower> (<alpha_lower> | <digit> | "_")* "@" \
            <decimal_literal>
            <alpha_lower>::= ["a"-"z"]
            <digit>::= ["0"-"9"]
            <decimal_literal>::= ["1"-"9"](["0"-"9"])*

        A formula is defined as follows::

            <expr>::= <var_symb> | "T" | "F" | "(" <unop> <expr> ")" | \
            "(" <expr> <binop> <exr> ")"
            <unop>::= "~"
            <binop>::= "&" | "|" | "->" | "<->"

        Parenthesis can be omitted as long as the interpretation is uniquely
        determined.
        Here, the precedence of logical operators is determined as follows::

            "~" > "&" > "|" > "->" > "<->"

        Operators of the same precedence are associated in such a way
        that binary operations are left-associative, unary operation
        is right-associative.
        """

        # The following tokens are suppressed in the parsed result.
        COMMA = pp.Suppress(cls.get_comma_tag())
        LPAREN = pp.Suppress(cls.get_lparen_tag())
        RPAREN = pp.Suppress(cls.get_rparen_tag())

        # Variable symbols are strings that match [a-z][a-z0-9_]*@[0-9]\+ .
        VAR = pp.Combine(pp.Word(pp.srange("[a-z]"), pp.srange("[a-z0-9_]")) \
                + "@" + pp.Word(pp.srange("[0-9]"), pp.srange("[0-9]")))

        TRUE = pp.Literal(cls.get_true_const_tag())
        FALSE = pp.Literal(cls.get_false_const_tag())
        CONST_REL = TRUE | FALSE

        ATOM_EXPR = VAR | CONST_REL

        UNOP = pp.Literal(cls.get_neg_tag())

        ANDOP = pp.Literal(cls.get_land_tag())
        OROP = pp.Literal(cls.get_lor_tag())
        IMPLIESOP = pp.Literal(cls.get_implies_tag())
        IFFOP = pp.Literal(cls.get_iff_tag())
        BINOP = pp.oneOf(" ".join(\
            [cls.get_land_tag(),cls.get_lor_tag(),\
            cls.get_implies_tag(),cls.get_iff_tag()]))

        @VAR.set_parse_action
        def action_var(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            res = tokens[0].split("@")
            assert len(res) == 2 and res[1].isdigit()
            NameMgr.lookup_index(res[0])
            if int(res[1]) < 1:
                raise Exception(
                    "Positional index of tokens[0] "
                    + "must be greater than or equal to 1."
                )
            return cls.var(NameMgr.lookup_index(tokens[0]))

        @CONST_REL.set_parse_action
        def action_const(string, location, tokens):
            if tokens[0] == cls.get_false_const_tag():
                return cls.false_const()
            if tokens[0] == cls.get_true_const_tag():
                return cls.true_const()
            assert False

        def action_unop(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            assert len(tokens[0]) == 2, f"{tokens[0]}"
            assert tokens[0][0] == cls.get_neg_tag(), f"{tokens[0]}"
            return cls.neg(tokens[0][1])

        def action_binop(string, location, tokens):
            # Accumulate in left-associative way.
            # Many tokens may be given at once when the same operation appears.
            assert len(tokens) == 1, f"{tokens}"
            accum = tokens[0][0]
            for i in range(2, len(tokens[0]), 2):
                accum = cls.binop(tokens[0][i - 1], accum, tokens[0][i])
            return accum

        # NOTE: Do not change the order of operators below,
        # which specifies the precedence of operators.
        EXPR = pp.Forward()
        EXPR <<= pp.infix_notation(
            ATOM_EXPR,
            [
                (UNOP, 1, pp.opAssoc.RIGHT, action_unop),
                (ANDOP, 2, pp.opAssoc.LEFT, action_binop),
                (OROP, 2, pp.opAssoc.LEFT, action_binop),
                (IMPLIESOP, 2, pp.opAssoc.LEFT, action_binop),
                (IFFOP, 2, pp.opAssoc.LEFT, action_binop),
            ],
            lpar=LPAREN,
            rpar=RPAREN,
        )
        return EXPR.parse_string(formula_str, parse_all=True)[0]

    def reduce_step(self, assoc: dict, st: BaseRelSt) -> None:
        """Performs reduce computation for this object."""
        if self.is_var_atom():
            assoc[id(self)] = self
            return
        super().reduce_step(assoc, st)

    def make_str_pre_step(self) -> str:
        """Makes string in prefix order for this object."""
        if self.is_var_atom():
            prop_index = self.get_atom_value(1)
            return f"{NameMgr.lookup_name(prop_index)}"
        return super().make_str_pre_step()

    def make_str_in_step(self) -> str:
        """Makes string in infix order for this object."""
        if self.is_var_atom():
            return ""
        return super().make_str_in_step()

    def make_str_post_step(self) -> str:
        """Makes string in postfix order for this object."""
        if self.is_var_atom():
            return ""
        return super().make_str_post_step()

    def make_node_str_step(self) -> str:
        """Makes string of this object for DOT print."""
        if self.is_var_atom():
            prop_index = self.get_atom_value(1)
            return f'"{NameMgr.lookup_name(prop_index)}"'
        return super().make_node_str_step()
