"""CNF Converter Class"""

import sys

from .name import NameMgr
from .baserelst import BaseRelSt
from . import op

class Cnf:
    """CNF Converter Class"""

    def __init__(self, expr_tup: tuple, st: BaseRelSt = None):
        """Constructs CNF from tuple of formulas with Tseitin transformation.

        Note:
            A tuple of propositional formulas is considered as conjunction
            of propositional formulas.

        Args:
            expr_tup: tuple of propositional formulas
            st: relational structure object (If given, coding information will
            be added to the header of DIMACS CNF)
        """

        self.st = st
        """structure (optional)"""

        self._dic = {}
        """dict to find encoded index from original index."""
        self._inv_list = []
        """list to find original index from encoded index."""

        self._expr_tup = expr_tup
        """tuple of propositional formulas"""
        base, naux, cnf = op.compute_cnf(expr_tup)

        if cnf == ():
            self._nvar = 0
            self._ncls = 0
            self._packed_cnf = ()
            return

        if cnf == ((),):
            self._nvar = 0
            self._ncls = 1
            self._packed_cnf = ((),)
            return

        result = [tuple([self.encode_lit(x) for x in cls]) for cls in cnf]
        self._nvar = max([max(map(abs, cls)) for cls in result])
        """number of variables"""
        assert self._nvar <= base + naux

        self._ncls = len(result)
        """number of clauses in CNF"""
        self._packed_cnf = tuple(result)
        """CNF, where variables are renumbered so that all indices from 1 to
        _nvar appear at least once in CNF."""
        self._base = base
        """maximum index of variables appearing in input formulas."""

    def encode_lit(self, lit: int) -> int:
        """Encodes literal.

        Args:
            lit: literal of an internal CNF variable.

        Returns:
            int: returns a literal of an external CNF variable.
        """
        var = abs(lit)
        if var not in self._dic:
            self._inv_list.append(var)
            self._dic[var] = len(self._inv_list)

        res = self._dic[var]
        return res if lit > 0 else -res

    def decode_lit(self, lit: int) -> int:
        """Decodes literal.

        Args:
            lit: literal of an external CNF variable

        Returns:
            int: literal of an internal CNF variable.
        """
        var = abs(lit)
        if not (0 < var <= len(self._inv_list)):
            raise IndexError

        res = self._inv_list[var - 1]
        return res if lit > 0 else -res

    def decode_assignment(self, assign: tuple[int]) -> tuple[int]:
        """Decodes assignment.

        Args:
            assign: assignment of external CNF variables

        Returns:
            tuple: assignment of internal CNF variables (but excluding
            auxilliary variables).
        """
        res = [self.decode_lit(x) for x in assign \
                        if abs(self.decode_lit(x)) <= self._base]
        return tuple(res)

    def get_nvar(self) -> int:
        """Gets the number of variables in CNF."""
        return self._nvar

    def get_ncls(self) -> int:
        """Gets the number of clauses in CNF."""
        return self._ncls

    def get_clause(self, pos: int) -> tuple[int]:
        """Gets clause of given position.

        Args:
            pos: position ranging from 0 to the number of clauses minus 1.
        """
        if not (0 <= pos < len(self._packed_cnf)):
            raise IndexError

        return self._packed_cnf[pos]

    def write(self, stream=None) -> None:
        """Write CNF in DIMACS CNF format.

        Args:
            stream: stream (stdout if not specified) to which CNF is written.
        """
        if stream == None:
            stream = sys.stdout

        dom = []
        if self.st != None:
            for pos, obj in enumerate(self.st.domain):
                code = self.st.get_code(obj)
                name = NameMgr.lookup_name(obj)
                dom.append(f"c dom {name}: "+" ".join(map(str, code)))

        enc = [
            f"c enc {i+1} {NameMgr.lookup_name(self.decode_lit(i+1))}"
            for i in range(self._nvar)
            if self.decode_lit(i + 1) <= self._base
        ]
        body = [" ".join(map(str, cls)) + " 0" for cls in self._packed_cnf]

        if stream != None:
            out = ""
            out += f"p cnf {self._nvar} {len(self._packed_cnf)}\n"
            for expr in self._expr_tup:
                out += f"c expr {op.to_str(expr)}\n"
            if self.st != None:
                out += "\n".join(dom+enc+body)
            else:
                out += "\n".join(enc+body)
            out += "\n"
            stream.write(out)
