Get Started
===========

Install Pygplib
-------------------

.. code:: shell-session

    $ pip install pygplib

    # The following third-party modules are necessary for solution sampling
    $ pip install python-sat
    $ pip install pyunigen

Quick Example
-------------

Let us randomly generate independent sets of size ``3`` in the following
graph, ``G``, with ``pygplib``.

.. code:: shell-session

    # V1 ------- V3
    # |          |
    # |          |
    # V2---V5    |
    # |    |     |
    # |    |     |
    # V4---V7   V6

Let us import necessary modules and create a graph structure.

.. code:: python

    from pygplib import Fog, op, GrSt, Cnf, Prop

    vertex_list = [1,2,3,4,5,6,7]                            # vertices of G
    edge_list = [(1,2),(1,3),(2,4),(2,5),(3,6),(4,7),(5,7)]  # edges of G
    st = GrSt(vertex_list, edge_list)

Let us parse an expression and construct a first-order formula object.
See :ref:`FirstOrderLogicofGraphs` and :ref:`FormatofFirstOrderFormula` for
details.

.. code:: python

    f = Fog.read("(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3)) "\
                +"& (~ x1=x2) & (~ x1=x3) & (~ x2=x3)")

Let us perform Boolean encoding for ``f`` and 
compute the domain constraint for each free variable of ``f``.
The list ``[g, ] + li`` consists of propositional formulas such that 
``f`` is satisfiable in ``G`` if and only if the conjunction of propositional formulas is
satisfiable.
Convert ``[g, ] + li`` to a canonical form, called a *Conjunctive Normal Form*
(*CNF* for short) by creating a Cnf object, ``mgr``.
The Cnf object is a manager for the converted CNF.
The encodings performed in this code block are described in more details in :ref:`EncodingFirstOrderFormula`.

.. code:: python

    g = op.perform_boolean_encoding(f, st)
    li  = [st.compute_domain_constraint(v) \
                    for v in op.get_free_vars(f)]
    mgr = Cnf( [g, ] + li, st=st)


Let us import ``pysat``, 
`a toolkit for SAT-based prototyping in Python <https://pysathq.github.io/>`__
, and ``unigen``, `UniGen approximately uniform sampler <https://github.com/meelgroup/unigen>`__ , 
and perform random sampling of solutions of the cnf. 

.. code:: python

    from pysat.formula import CNF
    from pysat.solvers import Solver
    from pyunigen import Sampler

    num=5 # number of samples to be generated

    sampler=Sampler()
    for clause in mgr.cnf:
        sampler.add_clause(clause)

    cells, hashes, samples = sampler.sample(num=num, sampling_set=range(1,mgr.base+1))
    for ext_partial_assign in samples:
        with Solver(\
            bootstrap_with=CNF(\
                from_clauses=\
                    list(mgr.cnf) + [(lit,) for lit in ext_partial_assign])) as solver:
            if solver.solve():
                ext_full_assign = solver.get_model() # external CNF vars.
                int_assign = mgr.decode_assignment(ext_full_assign) # internal CNF vars.
                fo_assign = st.decode_assignment(int_assign) # first-order vars.
                ans = sorted([st.object_to_vertex(fo_assign[key]) \
                                        for key in fo_assign.keys()])
                print(ans)
            else:
                print("Unexpected error occured during sampling!")

Sampling solutions of combinatrial problems is computationally hard in general.
To make the above computation more efficient, pygplib provides a technique of so-called symmetry breaking.
The formula of independent set is symmetry, i.e., any performulation of 
a satisfying assignment of vertices to first-order variables is also a solution of the formula,
which results in an enormous number of solutions, making it hard to perform sampling.
To overcome this, let us consider the following formula to which the constraint that all vertices assigned to variables are sorted is added instead of all-different constraint.

.. code:: python

    f = Fog.read("x1<x2 & x2<x3"\
                +"& (~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3)) ")

After that, let us encode it into CNF and perform sampling in the same way as described just above.
Sampling for larger graphs would become more efficient.
