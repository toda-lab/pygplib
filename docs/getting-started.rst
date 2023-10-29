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

Import necessary modules,
create a graph structure object of class ``GrSt`` with ``G``.

.. code:: python

    from pygplib import Fog, op, GrSt, Cnf, Prop

    vertex_list = [1,2,3,4,5,6,7]                            # vertices of G
    edge_list = [(1,2),(1,3),(2,4),(2,5),(3,6),(4,7),(5,7)]  # edges of G
    st = GrSt(vertex_list, edge_list)

Parse the expression of an independent set of size ``3`` 
and construct a first-order formula object, ``f``,
See, for first-order logic of graphs,
:ref:`FirstOrderLogicofGraphs` and, for formula format, :ref:`FormatofFirstOrderFormula`.

.. code:: python

    f = Fog.read("(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3)) "\
                +"& (~ x1=x2) & (~ x1=x3) & (~ x2=x3)")

Create a Cnf object, ``mgr``, from the first-order formula ``f`` via Boolean-encoding.
A *Conjunctive Normal Form* Formula (*CNF* for short) is a well-accepted canonical form of propositional formulas, 
and the Cnf object created is a manager for the CNF encoded from given propositional formulas.
It is initialized with a tuple of propositional formulas, ``(g, ) +
tup``, considering it as the conjunction of these formulas.
The encoding performed here is described in more details in
:ref:`EncodingFirstOrderFormula`.

.. code:: python

    g = op.propnize(f, st)
    tup  = tuple([st.compute_domain_constraint(v) \
                    for v in op.get_free_vars(f)])
    mgr = Cnf( (g, ) + tup , st)

Generate a CNF formula to file ``f.cnf`` in `DIMACS CNF format
<http://www.satcompetition.org/2009/format-benchmarks2009.html>`__ as follows.

.. code:: python

    with open("f.cnf","w") as out:
        mgr.write(stream=out)


To count the number of solutions, i.e., satisfying assignments
for the encoded CNF formula (``f.cnf`` in the current directory), 
download and build a model counter `sharpSAT <https://github.com/marcthurley/sharpSAT.git>`__ , 
a satisfiability tool to counter the number of satisfying assignments of a
CNF in DIMACS CNF format.
Run the following command.

.. code:: shell-session

    $ path-to-sharpSAT/sharpSAT f.cnf
    (The first part omited)
    # solutions 
    48
    # END
    
    time: 0.108726s

Note that solutions mean the permutations of all independent sets of size
``3`` because for example, the assignment ``x1=2,x2=7,x3=3`` is distinguished
from any other permutation of it, say ``x1=7,x1=2,x3=3``.
So the number of all independent sets of size ``3`` amounts to ``48/3!=8``.
