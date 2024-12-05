"""CNF Converter Class"""

import sys
from typing import Iterable

from .name import NameMgr
from .baserelst import BaseRelSt
from .absexpr import IndexGen
from . import op

class Cnf:

    """CNF Converter Class"""
    def __init__(self, li: Iterable,
        st: BaseRelSt = None,
        check_cnf: bool = False):
        """Constructs CNF from tuple/list of formulas with Tseitin transformation.

        Note:
            A list of propositional formulas is considered as conjunction
            of propositional formulas.

        Args:
            li: list of propositional formulas
            st: relational structure object
        """

        self._st = st
        """relational structure"""
        self._orig_base, naux, self._orig_cnf = op.compute_cnf(li)
        self._enc = {}
        """dictionary of encoded indices"""
        self._dec = {}
        """dictionary of decoded indices"""
        self.base = 0
        """number of decodable variables"""
        for clause in self._orig_cnf:
            for lit in clause:
                var = abs(lit)
                if self._st is not None\
                    and var <= self._orig_base\
                    and self._st.is_decodable_boolean_var(var)\
                    and var not in self._enc:
                    self.base += 1
                    self._enc[var]       = self.base
                    self._dec[self.base] = var
        self._idgen  = IndexGen(init_index=self.base+1)
        """index generator for undecodable variables"""
        # exceptional cases
        if self._orig_cnf == ():
            self.nvar = 0
            self.cnf = ()
            return
        if self._orig_cnf == ((),):
            self.nvar = 0
            self.cnf = ((),)
            return
        # Now, encode orig_cnf.
        self.cnf = tuple(\
            [tuple([self._encode_lit(x) for x in clause])\
                for clause in self._orig_cnf]\
        )
        """CNF, where variables are renumbered so that all indices from 1 to
        nvar appear at least once and all indices from 1 to base are decodable."""
        self.nvar = self.base + self._idgen.get_count()
        """maximum variable index""" 
        if check_cnf:
            self._check_cnf()

    def _check_cnf(self):
        # check nvar
        max_var = 0
        for clause in self.cnf:
            for lit in clause:
                var = abs(lit)
                max_var = var if max_var < var else max_var
        assert max_var == self.nvar, f"{max_var} == {self.nvar}"
        # check no missing variable
        checked_var = [False]*(self.nvar+1)
        for clause in self.cnf:
            for lit in clause:
                var = abs(lit)
                checked_var[var] = True
        assert False not in checked_var[1:]
        # check base
        if self._st is not None:
            for i in range(1,self.nvar+1):
                if i <= self.base:
                    assert self._dec[i] <= self._orig_base\
                        and self._st.is_decodable_boolean_var(self._dec[i])
                else:
                    assert self._dec[i] > self._orig_base\
                        or not self._st.is_decodable_boolean_var(self._dec[i])
        # check encoding
        decoded_cnf =\
            [tuple([self._decode_lit(x) for x in clause]) for clause in self.cnf]
        assert len(decoded_cnf) == len(self._orig_cnf)
        for i in range(len(decoded_cnf)):
            assert decoded_cnf[i] == self._orig_cnf[i]

    def _encode_lit(self, lit: int) -> int:
        """Encodes literal of internal variable to external one.

        Args:
            lit: literal of internal CNF variable.

        Returns:
            literal of external CNF variable.
        """
        var = abs(lit)
        if self._st is not None\
            and var <= self._orig_base\
            and self._st.is_decodable_boolean_var(var):
            assert var in self._enc
            assert self._dec[self._enc[var]] == var
        else:
            if var not in self._enc:
                ext_var = self._idgen.get_next()
                assert self.base < ext_var
                self._enc[var]     = ext_var
                self._dec[ext_var] = var
        ext_var = self._enc[var]
        return ext_var if lit > 0 else -ext_var

    def _decode_lit(self, lit: int) -> int:
        """Decodes literal of external variable to internal one.

        Args:
            lit: literal of external CNF variable

        Returns:
            literal of internal CNF variable.
        """
        var = abs(lit)
        int_var = self._dec[var]
        return int_var if lit > 0 else -int_var

    def decode_assignment(self, assign: Iterable) -> tuple[int]:
        """Decodes assignment.

        Args:
            assign: assignment of external CNF variables

        Returns:
            tuple: assignment of DECODATABLE internal CNF variables.
        """
        return tuple([self._decode_lit(x) for x in assign if x <= self.base])

    def get_nvar(self) -> int:
        """Gets the number of variables in CNF."""
        warn_msg = "`get_nvar()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return self.nvar

    def get_ncls(self) -> int:
        """Gets the number of clauses in CNF."""
        warn_msg = "`get_ncls()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        return len(self.cnf)

    def get_clause(self, pos: int) -> tuple[int]:
        """Gets clause of given position.

        Args:
            pos: position ranging from 0 to the number of clauses minus 1.
        """
        warn_msg = "`get_clause()` has been deprecated and will be removed in v3.0.0"
        warnings.warn(warn_msg, UserWarning)
        if not (0 <= pos < len(self.cnf)):
            raise IndexError
        return self.cnf[pos]

    def write(self, stream=None, format: str = "dimacs") -> None:
        """Write CNF in DIMACS CNF format.

        Args:
            stream: stream (stdout if not specified) to which CNF is written.
            format: file format of cnf
        """
        if self.nvar == 0 or len(self.cnf):
            raise Exception("cnf has no variable or no clause.")
        if stream == None:
            stream = sys.stdout
        if format != "dimacs":
            raise Exception(f"unknown format: {format}")
        if self._st is not None:
            dom = []
            for pos, obj in enumerate(self._st.domain):
                code = self._st.get_code(obj)
                name = NameMgr.lookup_name(obj)
                dom.append(f"c domain {name}: "+" ".join(map(str, code)))
            enc = [
                f"c enc {i+1} {NameMgr.lookup_name(self.decode_lit(i+1))}"
                for i in range(self.nvar)
                if self.decode_lit(i + 1) <= self.base
            ]
        body = [" ".join(map(str, clause)) + " 0" for clause in self.cnf]
        out = ""
        out += f"p cnf {self.nvar} {len(self.cnf)}\n"
        if self._st is not None:
            out += "\n".join(dom+enc+body)
        else:
            out += "\n".join(enc+body)
        out += "\n"
        stream.write(out)
