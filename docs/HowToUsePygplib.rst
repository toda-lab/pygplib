==========================
Using the pygplib module
==========================

:author: Takahisa Toda
:address: todat@acm.org

:revision: 2.0.0
:date: Nov., 2023

:copyright: Copyright |copy| 2003-2023 Takahisa Toda.

.. |copy| unicode:: 0xA9

:abstract: This document provides how-to instructions for the
    Python library for constructing, manipulating, 
    and encoding graph properties expressible with first-order logic of graphs.
    We mean by *graphs* graphs with no directed edge, no multiple edge, 
    no isolated edge, at most one isolated vertex, and no loop.

.. sectnum::    :depth: 4

.. contents::   :depth: 4

-----------


Parsing First-Order Formula
===========================

The ``pygplib`` mostly supports the format of untyped first-order formulas in
the `TPTP
format <https://www.tptp.org/Seminars/TPTPWorldTutorial/LogicFOF.html>`__
for automated theorem proving.
A first-order formula given in string can be parsed and constructed as 
a first-order formula object by ``Fog.read()``.
The format is detailed in `Format of First-Order Formula`_ .

.. code:: python

   from pygplib import Fog

   f = Fog.read("(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3))")


A first-order formula object can be converted back to string by ``op.to_str()``.

.. code:: python

   from pygplib import op

   assert op.to_str(f) == "(((~ edg(x1, x2)) & (~ edg(x1, x3))) & (~ edg(x2, x3)))"
   ff = Fog.read(op.to_str(f))
   assert f == ff

The resulted string is logically equivalent to the one just read, and 
the assertion holds in this case, however it should be noted that the 
object of a first-order formula simply represents the syntax of the formula 
and ``f == ff`` does not mean asserting the logical equivalence.
The above assertion holds simply because the precedence of ``&`` is 
interpreted as being left associative. 
Hence, the following formula ``fff``, explicitly specified
as being right associative, is recognized to be a different formula from
``f`` (and ``ff``).

.. code:: python

   fff = Fog.read("((~ edg(x1, x2)) & ((~ edg(x1, x3)) & (~ edg(x2, x3))))")
   assert f != fff

Note: when the class variables ``bipartite_order`` of ``Prop`` class and  
``Fog`` class are set ``True``, binary operations for these class objects 
with equal priority are associated, recursively halving them.

.. code:: python

    Fog.bipartite_order = False
    f = Fog.read("T & T & T & T")
    assert Fog.Fog.read(f) == "(((T & T) & T) & T)"
    Fog.bipartite_order = True
    f = Fog.read("T & T & T & T")
    assert Fog.Fog.read(f) == "((T & T) & (T & T))"
    Fog.bipartite_order = False

Similarly, when ``Prop.bipartite_order`` is set ``True``, 
``Prop`` objects computed by ``propnize()`` and ``compute_domain_constraint()`` 
become syntactically different expressions.

Name and Index of Symbol
------------------------

As soon as a formula is parsed, all variable symbols as well as constant
symbols appearing in the formula will be registered to NameManager class 
and unique indices are assigned.

.. code:: python

   from pygplib import NameMgr

   v = NameMgr.lookup_index("x1")
   name = NameMgr.lookup_name(v)
   assert "x1" == name

Reset NameManager, if necessary, by ``NameMgr.clear()`` to delete all
registered names and indices.

.. code:: python

   NameMgr.clear()
   assert not NameMgr.has_index("x1")
   v = NameMgr.lookup_index("x1") # new index is issued for the first time.
   assert NameMgr.has_index("x1")
   assert NameMgr.has_name(v)
   NameMgr.clear()
   assert not NameMgr.has_name(v)
   assert not NameMgr.has_index("x1")

The name of a variable symbol should begin with a lowercase letter,
followed by zero or more lower case letters, digits, or underscore,
while the name of a constant symbol should begin with an uppercase
letter, followed by zero or more uppercase letters, digits, or
underscore.

.. code:: python

   NameMgr.clear()
   v = NameMgr.lookup_index("x1")
   w = NameMgr.lookup_index("V1")
   assert NameMgr.is_variable(v)
   assert NameMgr.is_constant(w)

Constructing First-Order Formula
================================

An arbitrary well-formed formula can be constructed with built-in operations.

Basic Operations
----------------

.. code:: python

   v = NameMgr.lookup_index("x")
   w = NameMgr.lookup_index("y")
   f = Fog.edg(v,v)
   assert op.to_str(f) == "edg(x, y)"

   g = Fog.neg(Fog.eq(v,v))
   assert op.to_str(f) == "(~ x = y)"

   h = Fog.implies(f,g)
   assert op.to_str(h) == "(edg(x, y) -> (~ x = y))"


-  ``Fog.true_const()`` returns the true constant, ``T``.
-  ``Fog.false_const()`` returns the false constant ``F``.
-  ``Fog.neg(f)`` returns the negation of ``f``.
-  ``Fog.land(f,g)`` returns the AND of ``f`` and ``g``.
-  ``Fog.lor(f,g)`` returns the OR of ``f`` and ``g``.
-  ``Fog.implies(f,g)`` returns the implication from ``f`` to ``g``.
-  ``Fog.iff(f,g)`` returns the equivalence between ``f`` and ``g``.
-  ``Fog.forall(f,v)`` returns the formula in which all free occurrences
   of the name of ``v`` are universally quantified.
-  ``Fog.exists(f,v)`` returns the formula in which all free occurrences
   of the name of ``v`` are existentially quantified.
-  ``Fog.eq(v,w)`` returns the formula written as ``x=y`` in string,
   where ``x`` and ``y`` are the names of ``v`` and ``w``.
-  ``Fog.edg(v,w)`` returns the formula written as ``edg(x,y)`` in string, 
   where ``x`` and ``y`` are the names of ``v`` and ``w``.

Utility Functions and Advanced Operations
-----------------------------------------

Some utility functions and advanced operations for formulas
are listed below.

-  ``to_str(f)`` returns the string representation of formula object ``f``.
-  ``print_formula(f, stream=out, fmt=type)`` prints out formula object in
   stream (stdout if not given) in human-readable format (fmt=“str”) or
   DOT format (fmt=“dot”).
-  ``reduce(f)`` returns the result reduced from ``f`` with equivalent
   transformations to make it be as simple as possible.
-  ``get_free_vars_and_consts(f)`` returns a tuple of all
   free variables and constants of ``f``.
-  ``get_free_vars(f)`` returns a tuple of the indices of all free
   variables of ``f``.
-  ``propnize(f)`` returns an equivalent propositional formula of
   first-order formula ``f``. **Note: since this method performs
   quantifier elimination, it would take much time and space if a
   formula contains quantifiers and a graph is large.**
-  ``compute_cnf(tup)`` performs CNF-encoding for the conjunction of all
   ``Prop`` formulas in the tuple ``tup`` and returns a tuple of
   the followings:

   -  the maximum index of a variable in the input ``Prop`` formulas,
   -  the number of auxiliary variables introduced during encoding,
   -  a tuple of clauses, each clause is a tuple of variable indices.

As mentioned, we assume that a graph has no loop, and hence the formula
written as ``edg(x, x)`` is unsatisfiable.
The formula is evaluated to false constant by ``op.reduce()`` just like
``eval()`` does in arithmetic expression.

.. code:: python

   f = Fog.read("edg(x, x)")
   assert f != Fog.true_const() 
   assert op.reduce(f) == Fog.false_const()

However, ``op.reduce()`` only performs a few equivalent transformations 
and the resulted formula not always becomes irreducible, as demonstrated 
in the following code block.

.. code:: python

   f = Fog.read("edg(x, y) -> (~ x = y)")
   for v in op.get_free_vars(f):
       f = Fog.forall(f,v)

    assert op.to_str(f) == "(! [y] : (! [x] : (edg(x, y) -> (~ x = y))))"
    assert f != Fog.true_const() 

A formula can be printed out in DOT format, allowing us to visualize.

.. code:: python

   from pygplib import Fog
   from pygplib import op

   f = Fog.read("! [w] : (w=x1 | w=x2 | w=x3 | edg(w,x1) | edg(w,x2) | edg(w,x3))")
   with open("data/f.dot","w") as out:
       op.print_formula(f,stream=out,fmt="dot")

.. code:: shell-session

   $ dot -Tpng data/f.dot -o data/f.png

.. figure:: data/f.png
   :alt: data/f.png

   f.png

The above image depicts the data structure of a first-order formula. The
whole formula consists of objects of ``Fog`` class with the root node ``f``.

Creating Graph Structure
========================

In order to interpret first-order formula, it is necessary to create and
set graph structure to ``Fog`` class in advance. A graph structure is an
object of ``GrSt`` class, which manages domain of discourse and 
the interpretation of relation symbols over it.
Moreover ``GrSt`` class manages the encoding and decoding 
between first-order variables and CNF variables.

Currently there are different ways for the initialization of ``GrSt`` objects,
depending on the types of domain encoding: "edge encoding", 
"clique encoding", and "direct encoding".
These encodings simply differ in the binary encoding of each object 
in a domain.

The first example is the edge-encoding.
As commented in the following code block, each vertex is assigned 
a binary code (a row vector) of the matrix, which is a vertex-edge 
incidence matrix.

.. code:: python

   # V1 --- V2
   #  \    /
   #   \  /
   #    V3
   #   / \
   #  /   \
   # V4---V5
   vertex_list = [1,2,3,4,5]
   edge_list = [(1,2),(1,3),(2,3),(3,4),(3,5),(4,5)]
   #
   # V1 |1 1 0 0 0 0|
   # V2 |1 0 1 0 0 0|
   # V3 |0 1 1 1 1 0|
   # V4 |0 0 0 1 0 1|
   # V5 |0 0 0 0 1 1|
   Fog.st = GrSt(vertex_list, edge_list, encoding="edge", prefix="V")
   assert NameMgr.lookup_name(Fog.st.vertex_to_object(vertex_list[1])) == "V2"

As above, ``vertex_to_object()`` converts a vertex into a constant symbol
index. When ``GrSt`` object is initialized, such constant symbols are 
registered to ``NameMgr`` and their names begin with a given prefix, 
followed by a vertex index.
If a prefix is not given, default prefix is ``V``.

The second example is the clique-encoding.
The following matrix is a vertex-clique incidence matrix, where
the collection of cliques, designated by column vectors, is
a separating edge clique cover.
In general, the clique-encoding has size less than or equal 
to the edge-encoding.
The program for computing a separating edge clique cover is developed by the
author of ``pygplib``, but it is based on 
`heuristic algorithms by Conte et al <https://doi.org/10.1016/j.ic.2019.104464>`__ . 
Although the program `ECC8 <https://github.com/Pronte/ECC>`__ developed in Java 
by Conte is publicly available, it is not used to make ``pygplib``
self-contained and pure-Python module.

.. code:: python

   #
   # V1 |1 0 1 0|
   # V2 |1 0 0 0|
   # V3 |1 1 1 1|
   # V4 |0 1 0 0|
   # V5 |0 1 0 1|
   Fog.st = GrSt(vertex_list, edge_list, encoding="clique", prefix="V")

The third example is the direct-encoding (or one-hot encoding).
Given the following structure, a first-order variables is assigned vertex, 
say ``V2``, if and only if it has the code of high value at the
corresponding bit ``01000``.

.. code:: python

   # 
   # V1 |1 0 0 0 0|
   # V2 |0 1 0 0 0|
   # V3 |0 0 1 0 0|
   # V4 |0 0 0 1 0|
   # V5 |0 0 0 0 1|
   Fog.st = GrSt(vertex_list, edge_list, encoding="direct", prefix="V")

Note: Interpretation of Atoms
=============================

The following formulas are evaluated to true regardless of variables 
``x``, ``y``, and graph structures.

- ``~ edg(x, x)``
- ``edg(x, y) <-> edg(y, x)``
- ``x = x``
- ``x = y <-> y = x``


Encoding and Solving First-Order Formula
========================================

Let us now describe how first-order formulas can be encoded into CNFs with 
``pygplib`` and solved with ``pysat``, a toolkit for SAT-based prototyping 
in Python, or any other solver that conforms to the DIMACS CNF requirements.

In the following code block, a graph structure with a list of vertices 
``vertex_list`` and a list of edges ``edge_list`` is created and set to ``Fog``.
The first-order formula of an independent set of size ``3``, written as the conjunction of
``(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3))`` and 
``(~ x1=x2) & (~ x1=x3) & (~ x2=x3)``, is converted into a tuple
of objects of propositional formula class ``Prop`` ``(g, ) + tup``, 
with which ``Cnf`` object ``mgr`` is created.

.. code:: python

    from pygplib import Fog, op, GrSt, Cnf, Prop

    vertex_list = [1,2,3,4,5]
    edge_list = [(1,2),(1,3),(2,3),(3,4),(3,5),(4,5)]
    Fog.st = GrSt(vertex_list, edge_list, encoding="edge", prefix="V")
    f = Fog.read("(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3))")
    ff = Fog.read("(~ x1=x2) & (~ x1=x3) & (~ x2=x3)")
    fff = Fog.land(f,ff)
    g = op.propnize(fff)

    tup  = tuple([Fog.st.compute_domain_constraint(v) \
                    for v in op.get_free_vars(fff)])
    with open("data/t1.dot","w") as out:
        op.print_formula(tup[0],stream=out,fmt="dot")

    mgr = Cnf( (g, ) + tup )

In the following code block, which continues the above code block, 
``pysat`` module is imported in order to compute a 
satisfying assignment with a SAT solver.
The ``pygplib`` in itself does not provide any functionality of 
solving encoded formulas, and is independent of ``pysat`` module.
Please see `the instruction page <https://pysathq.github.io/installation/>`__ 
for the installation of ``pysat``.

.. code:: python

    from pysat.formula import CNF
    from pysat.solvers import Solver

    cnf = CNF(from_clauses=[mgr.get_clause(i) for i in range(mgr.get_ncls())])
    with Solver(bootstrap_with=cnf) as solver:
        if solver.solve():
            print("SATISFIABLE")
            ext_assign = solver.get_model() # external CNF vars.
            int_assign = mgr.decode_assignment(ext_assign) # internal CNF vars.
            fo_assign = Fog.st.decode_assignment(int_assign) # first-order vars.
            ans = [Fog.st.object_to_vertex(fo_assign[key]) \
                                    for key in fo_assign.keys()]
            print(ans) # list of vertices
        else:
            print("UNSATISFIABLE")

The output must be UNSATISFIABLE as the current graph has no independent set of size ``3``.

.. code:: python

    # V1 --- V2
    #  \    /
    #   \  /
    #    V3
    #   / \
    #  /   \
    # V4---V5

Recomputing the same formula for the following graph, we will in turn obtain an
independent set, say ``[7, 6, 1]``.

.. code:: python

    # V1 ------- V3
    # |          |
    # |          |
    # V2---V5    |
    # |    |     |
    # |    |     |
    # V4---V7   V6
    vertex_list = [1,2,3,4,5,6,7]
    edge_list = [(1,2),(1,3),(2,4),(2,5),(3,6),(4,7),(5,7)]

We will describe these code blocks in more details in the following sections
in terms of the Boolean encoding part, i.e. the computation of
``g`` and ``tup``, and ``Cnf`` class. 

Boolean Encoding
----------------------

We will describe why we consider not only ``g`` but also ``tup`` in the
previous code block. Remember that a first-order variable runs over
vertices (valid binary codes), in other words, a variable never runs
outside domain. To impose this (called *domain
constraints*) on first-order variables, we added ``tup``, a tuple of
propositional formulas of ``Prop`` class, one for each first-order variable, 
in the above code block.

.. code:: shell-session

   $ dot -Tpng data/t1.dot -o data/t1.png

.. figure:: data/t1.png
   :alt: data/t1.png

   The domain constraint for ``x3``

The above image depicts the domain constraint for ``x3``.
The ``tup`` consists of the constraints for ``x1``, ``x2``, and ``x3``.

In summary, the propositional formula encoded from ``fff`` amounts to the
conjunction of ``g``, ``tup[0],`` ``tup[1]``, and ``tup[2]``.

Cnf Class
--------------------------

In the initialization of ``Cnf`` object, the following method is executed, 
which is the main part of the CNF computation.

.. code:: python

   base, naux, cnf = op.compute_cnf( (g, ) + tup )

Besides this, a ``Cnf`` object manages the index mapping between 
variables in ``cnf`` above (*internal* CNF variables) and variables in the output
DIMACS CNF (*external* CNF variables).
This mapping is necessary if we need to encode so that there is no missing index.

A ``Cnf`` object provides the following instance methods.

- ``get_nvars()``: returns the number of CNF variables
- ``get_ncls()``: returns the number of clauses
- ``get_clause(i)``: returns the ``i``-th clause, a tuple of nonzero-integers,
  where ``i`` ranges from ``0`` to the number of clauses minus ``1``.
-  ``write(stream=stdout)``: generates a CNF in DIMACS format 
    to stream (``stdout`` if not given).
- ``decode_assignment(assign)``: decodes the assignment of DIMACS CNF
  variables (external CNF variables), ``assign``, 
  to the assignment of internal CNF variables except auxiliary ones.

In the following code block, the CNF manager ``mgr`` generates a CNF in 
DIMACS CNF format, which provides an alternative way to solve encoded
formulas with external solvers, say `kissat
<https://github.com/arminbiere/kissat>`__ , that conforms to 
`the DIMACS CNF requirements <http://www.satcompetition.org/2009/format-benchmarks2009.html>`__ .

.. code:: python

    with open("data/fff.cnf","w") as out:
        mgr.write(stream=out)

To decode a satisfying assignment, the header of the generated DIMACS CNF might
be useful.

.. code:: shell-session

    $ cat data/fff.cnf
    (The first part omitted)
    c enc 2 x1@1
    c enc 4 x2@1
    c enc 7 x1@2
    c enc 9 x2@2
    c enc 13 x1@3
    c enc 15 x2@3
    c enc 19 x1@4

Each line beginning with ``c enc`` shows the mapping between external CNF
variable indices and internal CNF variable names:
``c enc <dimacs_cnf_variable_index> <name_of_first_order_variable>@<bit>``
, where the name of an internal CNF variable is the concatenation of the
corresponding first-order variable and bit position.
For instance, the above header means that a first-order variable, say ``x1``,
is encoded in such a way that the first-bit ``x1@1`` is represented by 
DIMACS CNF variable ``2``, the second bit ``x1@2`` by ``4``, and so on.

The CNF computation is done by Tseitin transformation. 
There is a one-to-one correspondence between satisfying assignments 
of (external/internal) CNF variables and those of first-order variables.

Format of First-Order Formula
=============================

.. _Format of First-Order Formula:

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
