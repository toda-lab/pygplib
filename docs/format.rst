.. _Format of First-Order Formula:

Format of First-Order Formula
=============================

The ``pygplib`` mostly supports the format of untyped first-order formulas in
the `TPTP
format <https://www.tptp.org/Seminars/TPTPWorldTutorial/LogicFOF.html>`__
for automated theorem proving.

The following notation is useful shorthand.

-  ``e1 | e2 | e3 |`` … means a choice of ``e1``, ``e2``, ``e3``, etc.
-  ``( e )*`` means zero or more occurrences of ``e``.
-  ``["a"-"z"]`` matches any lowercase alphabet letter.
-  ``["A"-"Z"]`` matches any uppercase alphabet letter.
-  ``["0"-"9"]`` matches any digit from ``"0"`` to ``"9"``.
-  ``<word>`` means a non-terminal symbol.

The name of a *variable symbol* is defined as follows.

::

       <var_symb>::= <alpha_lower> (<alpha_lower> | <digit> | "_")*
       <alpha_lower>::= ["a"-"z"]
       <digit>::= ["0"-"9"]

The name of a *constant symbol* is defined as follows.

::

       <con_symb>::= <alpha_upper> (<alpha_upper> | <digit> | "_")*
       <alpha_upper>::= ["A"-"Z"]
       <digit>::= ["0"-"9"]

An *atomic formula* is defined as follows.

::

       <atom>::= <edg_atom> | <eq_atom> | <con_atom>
       <edg_atom>::= "edg" "(" <term> "," <term> ")"
       <eq_atom>::=  <term> "=" <term>
       <con_atom>::= "T" | "F"
       <term>::= <var_symb> | <con_symb>

A *first-order formula* is defined as follows.

::

       <expr>::= <atom> | "(" <unop> <expr> ")" | "(" <expr> <binop> <expr> ")" | "(" <qf> "[" <var> "]" ":" <expr> ")"
       <unop>::= "~"
       <binop>::= "&" | "|" | "->" | "<->"
       <qf>::= "!" | "?"

Parenthesis can be omitted as long as the interpretation is uniquely
determined. The precedence of logical operators is determined as
follows.

::

       "!"="?" > "~" > "&" > "|" > "->" > "<->"

Operators of the same precedence are associated in such a way that
binary operations are left-associative, unary operation and quantifiers
are right-associative.

Common Pitfalls
---------------

-  ``~ ! [x] : T`` means ``~ (! [x] : T)``.
-  ``! [x] : ~ T`` cannot be parsed: the parser attempts to interpret it
   as ``(! [x] : ~) T``. Write ``! [x] : (~ T)`` instead.
-  ``V12x`` is unacceptable as constant symbol name
    because uppercase and lowercase letters are mixed.
-  ``! [X] : T`` is unacceptable because X is interpreted as a constant
   symbol.
-  ``! [x,y] x=y`` is not supported: write ``! [x] : ! [y] : x=y``, which is
   equal to ``(! [x] : (! [y] : x = y))``.
-  ``! [x: vertex] x=x`` is unacceptable. typed variable is not supported.
-  ``x != x`` is not supported: write ``~ x = x`` instead.
-  ``! x = x`` is unacceptable: ``!`` is a universal quantifier.
-  ``edge(x=y)`` is unacceptable: Remove ``e`` from ``edge``.
