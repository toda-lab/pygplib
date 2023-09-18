"""Class of first-order logic of graphs"""

import functools

# The Pyparsing Module
# https://github.com/pyparsing/pyparsing/blob/master/docs/HowToUsePyparsing.rst
# https://pyparsing-docs.readthedocs.io/en/latest/pyparsing.html
import pyparsing as pp

from pygplib.absexpr  import AbsExpr
from pygplib.prop     import Prop
from pygplib.absfo    import AbsFo
from pygplib.st       import RelSt
from pygplib.name     import NameMgr


class Fo(AbsFo):
    """Expression of First-order logic of graphs

    Note:
        In the current implementation, syntactically identical subexpressions
        are shared. We have to keep it in mind that this might become source of
        bugs.
        For instance, consider (E x x) & x.
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
    _EQ  = "="

    _ATOM_TAGS  = AbsFo._ATOM_TAGS + (_EDG, _EQ)
    _BINOP_TAGS = AbsFo._BINOP_TAGS
    _UNOP_TAGS  = AbsFo._UNOP_TAGS
    _QF_TAGS    = AbsFo._QF_TAGS

    _EXPR_TAGS  = _ATOM_TAGS + _BINOP_TAGS + _UNOP_TAGS + _QF_TAGS

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
            return (0,)*cls._AUX_LEN

        if len(aux) == 3 and aux[1] > 0 and aux[2] > 0 \
            and NameMgr.lookup_name(aux[1]) > NameMgr.lookup_name(aux[2]):
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
        return cls(cls._EDG, aux=(0,x,y))

    @classmethod
    def eq(cls, x: int, y: int) -> AbsExpr:
        """Gets the atomic formula of the form x=y.

        Args:
            x: index of (variable or constant) symbol
            y: index of (variable or constant) symbol
        """
        if not (NameMgr.has_name(x) and NameMgr.has_name(y)):
            raise ValueError("Specified index of eq has no name.")
        return cls(cls._EQ, aux=(0,x,y))

    @classmethod
    def atom(cls, tag: str, x: int, y: int) -> AbsExpr:
        """Gets the tag-specified atomic formula.

        Args:
            x: index of (variable or constant) symbol (or 0 for true or false)
            y: index of (variable or constant) symbol (or 0 for true or false)
        """
        if tag not in cls._ATOM_TAGS:
            raise ValueError(\
                f"Expression tag, {tag}, is not available in {cls.__name__}")
        return cls(tag, aux=(0,x,y))


    # Instance Methods
    def get_atom_value(self, i: int) -> int:
        """Gets the term, specified by position, of the atomic formula.

        Args:
            i: position of term (1 or 2)
        """
        if not 0 < i <= type(self)._ATOM_LEN:
            raise IndexError(\
                f"Value index should range from 1 to {type(self)._ATOM_LEN}")
        return self._aux[type(self)._ATOM_BEGIN_POS + i - 1]

    def is_edg_atom(self) -> bool:
        """Is it an atom of the form edg(x,y) ?"""
        return self.get_tag() == type(self)._EDG

    def is_eq_atom(self) -> bool:
        """Is it an atom of the form x=y ?"""
        return self.get_tag() == type(self)._EQ

    def compute_nnf_step(self, negated: bool,
        s: list[list], t: list[list]) -> None:
        """Performs NNF computation for this object."""
        if self.is_edg_atom() or self.is_eq_atom():
            t.append([0, lambda : type(self).neg(self) if negated else self])
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

    def get_free_vars_and_consts_pre_step(self,\
        bound_vars: list, free_vars: list) -> None:
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

    def reduce_step(self, assoc: dict) -> None:
        """Performs reduce computatoin for this object."""

        if self.is_edg_atom():
            op = [self.get_atom_value(1), self.get_atom_value(2)]

            if op[0] == op[1]:  # edg(x,x) is always false regardless of graphs
                assoc[id(self)] = type(self).false_const()
                return

            if NameMgr.is_constant(op[0]) and NameMgr.is_constant(op[1]):
                if type(self).st is not None:
                    count = sum([1 if v*w == 1 else 0 for v, w in\
                        zip(type(self).st.get_code(op[0]),\
                            type(self).st.get_code(op[1]))])

                    if 0 < count < type(self).st.get_code_length():
                        assoc[id(self)] = type(self).true_const()
                        return
                    # count == type(self).st.get_code_length() cannot occur
                    # because we already checked if op[0] == op[1].
                    assert count == 0

                    assoc[id(self)] = type(self).false_const()
                    return

            assoc[id(self)] = self
            return

        if self.is_eq_atom():
            op = [self.get_atom_value(1), self.get_atom_value(2)]

            if op[0] == op[1]:  # x=x is always true regardless of graphs
                assoc[id(self)] = type(self).true_const()
                return

            if NameMgr.is_constant(op[0]) and NameMgr.is_constant(op[1]):
                if type(self).st is not None:
                    for v, w in\
                        zip(type(self).st.get_code(op[0]),\
                            type(self).st.get_code(op[1])):
                        if v != w:
                            assoc[id(self)] = type(self).false_const()
                            return
                    assoc[id(self)] = type(self).true_const()
                    return

            assoc[id(self)] = self
            return

        super().reduce_step(assoc)

    def propnize_step(self, assoc: dict, reorder: bool = False) -> None:
        """Performs propositionalization for this object."""
        def get_lit_list(index: int, st: RelSt) -> list:
            if NameMgr.is_constant(index):
                res = []
                for val in st.get_code(index):
                    res.append(Prop.true_const() if val == 1 \
                                                    else Prop.false_const())
                return res
            else:
                return [Prop.var(i) for i in st.get_prop_var_list(index)]

        if self.is_edg_atom():
            assert type(self).st is not None

            atom = [self.get_atom_value(1), self.get_atom_value(2)]

            # This is always false regardless of graphs
            if atom[0] == atom[1]:
                assoc[id(self)] = Prop.false_const()
                return

            left_li = get_lit_list(atom[0], type(self).st)
            right_li = get_lit_list(atom[1], type(self).st)

            # OR of bit-wise AND
            res_li = Prop.bitwise_binop(Prop.get_land_tag(), left_li, right_li)
            if reorder:
                acc1 = Prop.binop_batch(Prop.get_lor_tag(), res_li)
            else:
                acc1 = functools.reduce(lambda a, b: Prop.lor(a, b), res_li)

            # OR of bit-wise NOT IFF
            res_li = [Prop.neg(a) for a in\
                Prop.bitwise_binop(Prop.get_iff_tag(), left_li, right_li)]
            if reorder:
                acc2 = Prop.binop_batch(Prop.get_lor_tag(), res_li)
            else:
                acc2 = functools.reduce(lambda a, b: Prop.lor(a, b), res_li)

            assoc[id(self)] = Prop.land(acc1, acc2)
            return

        if self.is_eq_atom():
            atom = [self.get_atom_value(1), self.get_atom_value(2)]

            # This is always true regardless of graphs
            if atom[0] == atom[1]:
                assoc[id(self)] = Prop.true_const()
                return

            left_li = get_lit_list(atom[0], type(self).st)
            right_li = get_lit_list(atom[1], type(self).st)

            # AND of bit-wise IFF
            res_li = Prop.bitwise_binop(Prop.get_iff_tag(), left_li, right_li)
            if reorder:
                acc = Prop.binop_batch(Prop.get_land_tag(), res_li)
            else:
                acc = functools.reduce(lambda a, b: Prop.land(a, b), res_li)

            assoc[id(self)] = acc
            return

        if self.is_land_term() or self.is_lor_term()\
            or self.is_implies_term() or self.is_iff_term():
            left = assoc[id(self.get_operand(1))]
            right = assoc[id(self.get_operand(2))]
            assoc[id(self)] = Prop.binop(self.get_tag(), left, right)
            return

        if self.is_neg_term():
            op = assoc[id(self.get_operand(1))]
            assoc[id(self)] = Prop.neg(op)
            return
        if self.is_true_atom():
            assoc[id(self)] = Prop.true_const()
            return
        if self.is_false_atom():
            assoc[id(self)] = Prop.false_const()
            return

        assert False


    # Parser
    @classmethod
    def read(cls, formula_str: str, reorder: bool = False) -> AbsExpr:
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
                            | "(" <qf> <var> <expr> ")"
            <unop>::= "!"
            <binop>::= "&" | "|" | "->" | "<->"
            <qf>::= "A" | "E"

        Parenthesis can be omitted as long as the interpretation is uniquely
        determined.
        Here, the precedence of logical operators is determined as follows::

            "A"="E" > "!" > "&" > "|" > "->" > "<->"

        Operators of the same precedence are associated in such a way
        that binary operations are left-associative, unary operation and
        quantifiers are right-associative.

        Note:
            ! A x T means ! (A x T), but A x ! T cannot be parsed because the
            parser attempts to interprete it as (A x !) T due to precedence,
            unless I misunderstand.

        Args:
            formula_str: string representation of formula
            reorder: True if the order of operations to be applied is changed.
        """

        def action_tag(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            return str(tokens[0])

        def action_var_symb(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            return NameMgr.lookup_index(tokens[0])

        def action_con_symb(string, location, tokens):
            assert len(tokens) == 1, f"{tokens}"
            return NameMgr.lookup_index(tokens[0])

        def action_con_rel(string, location, tokens):
            if tokens[0] == cls.get_false_const_tag():
                return cls.false_const()
            if tokens[0] == cls.get_true_const_tag():
                return cls.true_const()
            assert False

        def action_edg_rel(string, location, tokens):
            if tokens[0] == cls.get_edg_tag():
                op1 = int(tokens[1])
                op2 = int(tokens[2])
                return cls.edg(op1, op2)
            assert False

        def action_eq_rel(string, location, tokens):
            if tokens[1] == cls.get_eq_tag():
                op1 = int(tokens[0])
                op2 = int(tokens[2])
                return cls.eq(op1, op2)
            assert False

        def action_qfop(string, location, tokens):
            assert len(tokens[0]) == 3, f"{tokens}"
            return cls.qf(tokens[0][0], tokens[0][2], tokens[0][1])

        def action_negop(string, location, tokens):
            assert len(tokens[0]) == 2, f"{tokens}"
            return cls.neg(tokens[0][1])

        def action_binop(string, location, tokens):
            # Accumulate tokens in left-associative way.
            # Many tokens may be given at once when the same operation appears.
            accum = tokens[0][0]
            for i in range(2, len(tokens[0]), 2):
                accum = cls.binop(tokens[0][i-1], accum, tokens[0][i])
            return accum

        def action_binop_batch(string, location, tokens):
            assert False not in [tokens[0][i] == tokens[0][1]\
                for i in range(1, len(tokens[0]), 2)]
            expr_li = [tokens[0][i] for i in range(0, len(tokens[0]), 2)]
            return cls.binop_batch(tokens[0][1], expr_li)

        # The following tokens are suppressed in the parsed result.
        COMMA   = pp.Suppress(cls.get_comma_tag())
        LPAREN  = pp.Suppress(cls.get_lparen_tag())
        RPAREN  = pp.Suppress(cls.get_rparen_tag())

        # Literal will match the given string,
        # even if it is just the start of a larger string.
        AND     = pp.Literal(cls.get_land_tag()).set_parse_action(action_tag)
        OR      = pp.Literal(cls.get_lor_tag()).set_parse_action(action_tag)
        NEG     = pp.Literal(cls.get_neg_tag()).set_parse_action(action_tag)
        IMPLIES = pp.Literal(
            cls.get_implies_tag()).set_parse_action(action_tag)
        IFF     = pp.Literal(cls.get_iff_tag()).set_parse_action(action_tag)
        EQ      = pp.Literal(cls.get_eq_tag()).set_parse_action(action_tag)

        # Keyword will only match the given string
        # if it is not part of a larger word
        # (followed by space, or by a non-word character).
        ALL     = pp.Keyword(cls.get_forall_tag()).set_parse_action(action_tag)
        EXISTS  = pp.Keyword(cls.get_exists_tag()).set_parse_action(action_tag)
        EDG     = pp.Keyword(cls.get_edg_tag()).set_parse_action(action_tag)
        TRUE    = pp.Keyword(
            cls.get_true_const_tag()).set_parse_action(action_tag)
        FALSE   = pp.Keyword(
            cls.get_false_const_tag()).set_parse_action(action_tag)

        # Variables are strings that match the pattern [a-z][a-z_0-9]* .
        VAR_SYMB = pp.Word(
            pp.alphas.lower(),
            pp.alphas.lower()+pp.nums+"_").set_parse_action(action_var_symb)

        # Constants are strings that match the pattern [A-Z][A-Z_0-9]* .
        CON_SYMB = pp.Word(
            pp.alphas.upper(),
            pp.alphas.upper()+pp.nums+"_").set_parse_action(action_con_symb)

        # No constant symbol and no function symbol.
        TERM  = VAR_SYMB | CON_SYMB

        # Relation Symbols: "edg", "="
        EDG_REL = (EDG + LPAREN + TERM +
            COMMA + TERM + RPAREN).set_parse_action(action_edg_rel)
        EQ_REL  = (TERM + EQ + TERM).set_parse_action(action_eq_rel)
        CON_REL = (TRUE | FALSE).set_parse_action(action_con_rel)
        ATOM  = EDG_REL | EQ_REL | CON_REL

        QF    = (ALL | EXISTS) + VAR_SYMB

        EXPR  = pp.Forward()

        # NOTE: Do not change the order of operators below,
        # which specifies the precedence of operators.
        EXPR <<= pp.infix_notation(
            ATOM,
            [
                (QF,      1, pp.opAssoc.RIGHT, action_qfop),
                (NEG,     1, pp.opAssoc.RIGHT, action_negop),
                (AND,     2, pp.opAssoc.LEFT,  action_binop_batch if reorder
                else action_binop),
                (OR,      2, pp.opAssoc.LEFT,  action_binop_batch if reorder
                else action_binop),
                (IMPLIES, 2, pp.opAssoc.LEFT,  action_binop),
                (IFF,     2, pp.opAssoc.LEFT,  action_binop),
            ],
            lpar=cls.get_lparen_tag(),
            rpar=cls.get_rparen_tag()
        )

        return EXPR.parse_string(formula_str, parse_all = True)[0]


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

            op1  = NameMgr.lookup_name(self.get_atom_value(1)) \
                if self.get_atom_value(1) != 0 else "-"
            op2  = NameMgr.lookup_name(self.get_atom_value(2)) \
                if self.get_atom_value(2) != 0 else "-"

            return f"\"edg({op1},{op2})\"" \
                if self.is_edg_atom() else f"\"{op1}={op2}\""

        return super().make_node_str_step()
