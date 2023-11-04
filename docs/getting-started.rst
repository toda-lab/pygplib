Get Started
===========

Install Pygplib
-------------------

.. code:: shell-session

    $ pip install pygplib

Quick Example
-------------

Let us count the number of independent sets of size ``3`` in the following
graph, ``G``, with ``pygplib``.

.. code:: shell-session

    # V1 ------- V3
    # |          |
    # |          |
    # V2---V5    |
    # |    |     |
    # |    |     |
    # V4---V7   V6

Import necessary modules and create a graph structure.

.. code:: python

    from pygplib import Fog, op, GrSt, Cnf, Prop

    vertex_list = [1,2,3,4,5,6,7]                            # vertices of G
    edge_list = [(1,2),(1,3),(2,4),(2,5),(3,6),(4,7),(5,7)]  # edges of G
    st = GrSt(vertex_list, edge_list)

Parse an expression and construct a first-order formula object.
See :ref:`FirstOrderLogicofGraphs` and :ref:`FormatofFirstOrderFormula` for
details.

.. code:: python

    f = Fog.read("(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3)) "\
                +"& (~ x1=x2) & (~ x1=x3) & (~ x2=x3)")

Perform Boolean encoding for ``f`` and 
compute the domain constraint for each free variable of ``f``.
The tuple ``(g, ) + tup`` consists of propositional formulas such that 
``f`` is satisfiable in G if and only if the conjunction of propositional formulas is
satisfiable.
Convert ``(g, ) + tup`` to a canonical form, called a *Conjunctive Normal Form*
(*CNF* for short) by creating a Cnf object, ``mgr``.
The Cnf object is a manager for the converted CNF.
The encodings performed in this code block are described in more details in :ref:`EncodingFirstOrderFormula`.

.. code:: python

    g = op.perform_boolean_encoding(f, st)
    tup  = tuple([st.compute_domain_constraint(v) \
                    for v in op.get_free_vars(f)])
    mgr = Cnf( (g, ) + tup )

Generate a CNF formula to ``f.cnf`` in `DIMACS CNF format
<http://www.satcompetition.org/2009/format-benchmarks2009.html>`__ .

.. code:: python

    with open("f.cnf","w") as out:
        mgr.write(stream=out)


To count the number of solutions, 
download and build a model counter `sharpSAT
<https://github.com/marcthurley/sharpSAT.git>`__ .
Run the following command.

.. code:: shell-session

    $ path-to-sharpSAT/sharpSAT f.cnf
    (The first part omitted)
    # solutions 
    48
    # END
    
    time: 0.108726s

Note that solutions are the permutations of all independent sets of size
``3``.
For example, the assignment ``x1=2,x2=7,x3=3`` is distinguished
from any other permutation of it, say ``x1=7,x1=2,x3=3``.
Hence the number of all independent sets of size ``3`` amounts to ``48/3!=8``.
