"""Operations for traversing, manipulating, and converting formulas"""

import sys
import functools

from .absexpr  import AbsExpr
from .absexpr  import IndexGen
from .prop     import Prop
from .absfo    import AbsFo
from .name     import NameMgr
from .baserelst import BaseRelSt

# Common Methods
def generator(f: AbsExpr, skip_shared: bool = False):
    """Yeilds all subformulas with left subformula first.

    If skip_shared is set True, shared subformulas are
    skipped, that is, if there are multiple occurrences of
    a synactically identical subformula, the second or later
    occurences of each such subformula are ignored.

    Note:
        It would be safe to call generator with skip_shared False for
        first-order formulas. Consider, for instance,  (? [x] : x) & x.
        Since the second and the third occurrences of x are shared,
        the third occurence of x is skipped if skip_shared is enabled.
        However, there are cases for which the third one should be treated
        separately from the second one.
        For instance, consider computing all free variables from the above
        formula. If the third occurrence of x is skipped, no free variable
        will be mistakenly output.

    Args:
        f: formula to be traversed
        skip_shared: indicates whether shared formulas are skipped.

    Yields:
        (i, subexpr): when subexpr appears in prefix order (for i=0),
        in infix order (for i=1), and in postfix order (for i=2).
    """
    done = set()  # sub-formulas are added in postfix-order
    s = []  # backtracking stack
    subexpr = f

    while True:
        if subexpr.is_atom_term() or (skip_shared and subexpr in done):

            if not (skip_shared and subexpr in done):
                yield (0, subexpr)

            # backtrack
            while True:
                if not (skip_shared and subexpr in done):
                    done.add(subexpr)
                    yield (2, subexpr)
                if s == []:
                    return
                i, subexpr = s.pop()
                assert not (skip_shared and subexpr in done)
                if i == 0 and subexpr.is_binop_term():
                    s.append([1, subexpr])
                    yield (1, subexpr)
                    # right subformula
                    subexpr = subexpr.get_operand(2)
                    break
        else:
            s.append([0, subexpr])
            yield (0, subexpr)
            # left subformula first
            subexpr = subexpr.get_operand(1)


def to_str(f: AbsExpr) -> str:
    """Converts formula into string.

    The same formula can be constructed, by read(), from the string
    produced by this method.
    """
    out = ""

    for i, subexpr in generator(f):
        if i == 0:
            out += subexpr.make_str_pre_step()
        elif i == 1:
            out += subexpr.make_str_in_step()
        elif i == 2:
            out += subexpr.make_str_post_step()

    return out


def print_formula(f: AbsExpr, stream=None, graph_name="output", fmt="str") -> None:
    """Prints formula to stream (stdout if not given).

    Args:
        f: formula
        stream: stream (stdout if None)
        graph_name: name of graph in DOT format
        format: human-readble format "str" or DOT format "dot"
    """
    if stream == None:
        stream = sys.stdout

    if fmt == "str":
        stream.write(to_str(f) + "\n")
        return

    if fmt != "dot":
        raise Exception(f"invalid format {format}")

    out = "digraph " + f"{graph_name}" + " {\n"
    for i, g in generator(f, skip_shared=True):
        if i == 0:
            out += "\t" + f"{id(g)} [label = {g.make_node_str_step()}]\n"
        elif i == 1:
            continue
        elif i == 2:
            if g.is_binop_term():
                out += f"\t{id(g)}" + " -> " + f"{id(g.get_operand(1))}\n"
                out += f"\t{id(g)}" + " -> " + f"{id(g.get_operand(2))}\n"
            elif g.is_unop_term():
                out += f"\t{id(g)}" + " -> " + f"{id(g.get_operand(1))}\n"
            elif g.is_atom_term():
                continue
            elif isinstance(g, AbsFo) and g.is_qf_term():
                out += f"\t{id(g)}" + " -> " + f"{id(g.get_operand(1))}\n"
            else:
                raise Exception(f"unexpected term: {g.gen_key()}")

    if stream != None:
        out += "}\n"
        stream.write(out)


def compute_nnf(f: AbsExpr) -> AbsExpr:
    """Computes negation normal form (NNF).

    The iff and implies operators, if any, will be excluded in the output
    formula.

    Args:
        f:  formula to be converted.
    """

    def _build_formula_posfix(t: list) -> AbsExpr:
        s = []
        while t != []:
            i, func = t.pop()
            if i == 0:
                s.append(func())
                continue

            if i == 1:
                left = s.pop()
                s.append(func(left))
                continue

            if i == 2:
                right = s.pop()
                left = s.pop()
                s.append(func(left, right))
                continue

            assert False
        assert len(s) == 1
        return s[0]

    s = []  # formulas to be computed
    t = []  # operators in nnf in postfix order
    s.append([False, f])
    while s != []:
        negated, g = s.pop()
        g.compute_nnf_step(negated, s, t)
    return _build_formula_posfix(t)


def reduce(f: AbsExpr, st: BaseRelSt = None) -> AbsExpr:
    """Reduces it into as simple formula as possible, retaining equivalence.

    Quantifiers are not eliminated except for constant operands.
    Relational structure is not mandatory.
    If relational structure is set, it reduces constant symbols
    as much as possible.

    Args:
        f:  formula to be reduced

    Note:
        The behaviour of this method changes depending on structures.
    """
    nnf = compute_nnf(f)

    assoc = {}
    for i, g in generator(nnf, skip_shared=True):
        if i != 2:
            continue
        if id(g) in assoc:
            continue
        g.reduce_step(assoc, st)

    assert id(nnf) in assoc
    return assoc[id(nnf)]


# First-Order Logic Methods
def get_free_vars_and_consts(expr: AbsFo) -> tuple:
    """Gets all free variables and constant symbols."""
    if not issubclass(type(expr), AbsFo):
        raise TypeError("Expression must be an instance of AbsFo or its subclass")

    bound_vars = []  # bound variables
    free_vars = []  # free variables and constaints
    # Note: Do not make skip_shared True. Otherwise, the method,
    # when applied to say (? [x] : x) & x, mistakenly returns no free variable.
    for i, g in generator(expr):
        if i == 0:
            g.get_free_vars_and_consts_pre_step(bound_vars, free_vars)
            continue
        if i == 2:
            g.get_free_vars_and_consts_post_step(bound_vars, free_vars)
            continue
    assert bound_vars == []
    return tuple(set(free_vars))


def get_free_vars(expr: AbsFo) -> tuple:
    """Gets all free variables from the formula."""
    res = get_free_vars_and_consts(expr)
    return tuple([i for i in res if NameMgr.is_variable(i)])


def substitute(expr: AbsFo, y: int, x: int) -> AbsFo:
    """Substitutes y for all free occurences of x.

    Args:
        expr:   formula
        y:  index of (variable or constant) symbol
        x:  index of (variable or constant) symbol
    """
    if not issubclass(type(expr), AbsFo):
        raise TypeError("Expression must be an instance of AbsFo or its subclass")
    if not NameMgr.has_name(y):
        raise ValueError(f"No name of index {y}")
    if not NameMgr.has_name(x):
        raise ValueError(f"No name of index {x}")

    nof_bound = 0
    assoc = {}
    # Note: Do not make skip_shared True. Otherwise, the method,
    # when applied to say (? [x] : x) & x, mistakenly returns (? [x] : x) & x.
    # The correct result must be (? [x] : x) & y.
    for i, g in generator(expr):
        if i == 0:
            if g.is_forall_term() or g.is_exists_term():
                if g.get_bound_var() == x:
                    nof_bound += 1
            continue
        if i == 2:
            if g.is_forall_term() or g.is_exists_term():
                if g.get_bound_var() == x:
                    nof_bound -= 1
            if id(g) in assoc:
                continue
            if nof_bound == 0:
                g.substitute_step(y, x, assoc)
            continue
    assert nof_bound == 0
    assert id(expr) in assoc
    return assoc[id(expr)]


def _eliminate_qf_step(
    expr: AbsFo, const_symb_tup: tuple, assoc: dict) -> None:
    """Performs quantifier elimination for this object.

    Note: We did not distribute this method over formula classes
    because otherwise, substitute(), called by this method, requires
    to import op module, which results in circular import.
    """

    if expr.is_neg_term():
        g = assoc[id(expr.get_operand(1))]
        assoc[id(expr)] = type(expr).neg(g)
        return

    if expr.is_true_atom() or expr.is_false_atom():
        assoc[id(expr)] = expr
        return

    if (
        expr.is_land_term()
        or expr.is_lor_term()
        or expr.is_implies_term()
        or expr.is_iff_term()
    ):
        left = assoc[id(expr.get_operand(1))]
        right = assoc[id(expr.get_operand(2))]
        assoc[id(expr)] = type(expr).binop(expr.get_tag(), left, right)
        return

    if expr.is_forall_term() or expr.is_exists_term():
        bvar = expr.get_bound_var()
        g = assoc[id(expr.get_operand(1))]

        li = [substitute(g, d, bvar) for d in const_symb_tup]

        if type(expr).bipartite_order:
            if expr.is_forall_term():
                acc = type(expr).binop_batch(type(expr).get_land_tag(), li)
            else:
                acc = type(expr).binop_batch(type(expr).get_lor_tag(), li)
        else:
            if expr.is_forall_term():
                acc = functools.reduce(lambda a, b: type(expr).land(a, b), li)
            else:
                acc = functools.reduce(lambda a, b: type(expr).lor(a, b), li)

        assoc[id(expr)] = acc
        return

    if expr.is_edg_atom() or expr.is_eq_atom():
        assoc[id(expr)] = expr
        return

    assert False


def eliminate_qf(expr: AbsFo, st: BaseRelSt) -> AbsFo:
    """Performs quantifier elimination.

    Args:
        expr:   formula to which elimination is performed.

    Note:
        The behaviour of this method changes depending on structures.

    Raises:
        Exception:  if no relational structure is set (i.e. None).
    """
    if not issubclass(type(expr), AbsFo):
        raise TypeError("Expression must be an instance of AbsFo or its subclass")
    if st == None:
        raise Exception("Set relational structure")
    const_symb_tup = st.domain

    assoc = {}
    for i, g in generator(expr):
        if i != 2:
            continue
        if id(g) in assoc:
            continue
        _eliminate_qf_step(g, const_symb_tup, assoc)

    assert id(expr) in assoc
    return assoc[id(expr)]


def propnize(f: AbsFo, st: BaseRelSt) -> Prop:
    """Converts a first-order formula into an equiv. propositional formula.

    Args:
        f:  first-order formula

    Returns:
        Prop:   propositional formula

    Note:
        The behaviour of this method changes depending on structures.

    Raises:
        Exception:  if no relational structure is set (i.e. None).
    """
    if not issubclass(type(f), AbsFo):
        raise TypeError("Expression must be an instance of AbsFo or its subclass")

    qf_free = eliminate_qf(f, st)

    assoc = {}
    for i, g in generator(qf_free, skip_shared=True):
        if i != 2:
            continue
        if id(g) in assoc:
            continue
        g.propnize_step(assoc, st)

    assert id(qf_free) in assoc
    return assoc[id(qf_free)]



# Propositional Logic Methods
def compute_cnf(tup: tuple) -> tuple[int, int, tuple[tuple[int, ...], ...]]:
    """Computes Conjunction Normal Form for the tuple of formulas.

    Note:
        Auxiliary variables introduced during CNF-encoding are
        consecutively assigned indices, starting with the maximum index of
        a Boolean variable in input formesssions plus one.
        The output CNF consists of indices of Boolean variables in input
        propositional formulas and indices of auxiliary variables.

    Returns:
        (int,int,tuple): a tuple containing, respectively,

        * the maximum index of a Boolean variable in input formulas,
        * the number of auxiliary variables introduced during CNF-encoding,
        * a tuple of clauses, each clause is a tuple of variable indices.
    """
    if type(tup) is not tuple:
        raise TypeError("Tuple of Props must be given as input argument.")
    if tup == ():
        raise TypeError("Tuple must be non-empty")
    if False in [issubclass(type(f), Prop) for f in tup]:
        raise TypeError(
            "Expression must be \
            an instance of Prop or its subclass"
        )

    expr_list = [reduce(f) for f in tup]

    if type(tup[0]).false_const() in expr_list:
        return 0, 0, ((),)  # UNSAT

    # the largest index of variables appearing in formulas
    base = 0
    for f in expr_list:
        var_list = [
            g.get_var_index()
            for i, g in generator(f, skip_shared=True)
            if i == 2 and g.is_var_atom()
        ]
        if var_list != []:
            val = max(var_list)
            base = val if base < val else base

    # next index of aux. variable
    igen = IndexGen(base + 1)
    cnf = []

    for f in expr_list:
        if f.is_true_atom():
            continue
        assoc = {}
        for i, g in generator(f, skip_shared=True):
            if i != 2:
                continue
            if id(g) in assoc:
                continue
            g.compute_cnf_step(igen, assoc, cnf)

        assert id(f) in assoc
        cnf.append((assoc[id(f)],))

    naux = igen.get_count()  # nof aux. variables
    return base, naux, tuple(cnf)
