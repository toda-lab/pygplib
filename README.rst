Pygplib: Python First-Order Graph Property Library
==================================================

|Test| |Coverage| |License|

Introduction
============

*Pygplib* (Python First-Order Graph Property Library) is a Python module 
for constructing, manipulating, and encoding graph properties expressible 
with first-order logic of graphs.
We mean by *graphs* graphs with no directed edge, no multiple edge, 
no isolated edge, at most one isolated vertex, and no loop.

Documentation
=============

See `pygplib’s documentation <https://pygplib.readthedocs.io/en/latest/>`__ .

Examples
========

The ``pygplib`` serves as a prototyping tool to tackle with 
various graph related applications.
It provides access to state-of-the-art satisfiability technologies 
without advanced knowledge.
Basic steps to follow are :

- Express a graph property of interest as a first-order formula.
- Encode it and a graph structure into CNF, 
  a canonical normal form for propositional formulas, with  ``pygplib``.
- Apply satisfiability tools to the CNF to compute satisfying
  assignments.
- Decode the result into the assignment to first-order variables with
  ``pygplib``.

Note: the current version remains in an experimental stage with scalability issues.


Encoding First-Order Expressible Property
-----------------------------------------

In the following code block, a graph structure object of ``GrSt`` class 
with a list of vertices 
``vertex_list`` and a list of edges ``edge_list`` is created and set to 
first-order formula of graphs class ``Fog``.
The first-order formula of an independent set of size ``3``, 
written as 
``(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3)) & (~ x1=x2) & (~ x1=x3) & (~
x2=x3)``, is converted into a tuple of ``Prop`` formula objects ``(g, ) + tup``, 
with which ``Cnf`` object ``mgr`` is created.
The CNF encoded from ``f`` is generated to ``data/f.cnf`` in 
`DIMACS CNF format <http://www.satcompetition.org/2009/format-benchmarks2009.html>`__ .

.. code:: python

    from pygplib import Fog, op, GrSt, Cnf, Prop

    # V1 ------- V3
    # |          |
    # |          |
    # V2---V5    |
    # |    |     |
    # |    |     |
    # V4---V7   V6
    vertex_list = [1,2,3,4,5,6,7]
    edge_list = [(1,2),(1,3),(2,4),(2,5),(3,6),(4,7),(5,7)]

    Fog.st = GrSt(vertex_list, edge_list, encoding="edge", prefix="V")
    f = Fog.read("(~ edg(x1,x2)) & (~ edg(x1,x3)) & (~ edg(x2,x3)) & (~ x1=x2) & (~ x1=x3) & (~ x2=x3)")
    g = op.propnize(f)

    tup  = tuple([Fog.st.compute_domain_constraint(v) \
                    for v in op.get_free_vars(f)])
    mgr = Cnf( (g, ) + tup )
    with open("data/f.cnf","w") as out:
        mgr.write(stream=out)

Solving First-Order Expressible Property
----------------------------------------

In the following code block, which continues the previous code block, 
a solution satisfying the current first-order formula ``f``, i.e. a vertex assignment to first-order
variables ``x1``, ``x2``, and ``x3``, can be computed with ``pysat``, 
`a toolkit for SAT-based prototyping in Python <https://pysathq.github.io/>`__ .
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

In the following code block, all solutions can be enumerated.

.. code:: python

    from pysat.formula import CNF
    from pysat.solvers import Solver

    cnf = CNF(from_clauses=[mgr.get_clause(i) for i in range(mgr.get_ncls())])
    with Solver(bootstrap_with=cnf) as solver:
        for ext_assign in solver.enum_models():
            int_assign = mgr.decode_assignment(ext_assign) # internal CNF vars.
            fo_assign = Fog.st.decode_assignment(int_assign) # first-order vars.
            ans = [Fog.st.object_to_vertex(fo_assign[key]) \
                                    for key in fo_assign.keys()]
            print(ans) # list of vertices

The output is as follows.
Note that `[7,6,1]` and `[7,1,6]` are distinguished because they diff
in the assignments to `x2` and `x3`.
Solutions here mean the permutations of all independent sets of size ``3``.


.. code:: shell-session

    [7, 6, 1]
    [7, 2, 3]
    [7, 2, 6]
    [5, 1, 4]
    [5, 1, 6]
    [7, 1, 6]
    (The remaining part omitted)

The number of solutions can be exactly counted by model counters such as `sharpSAT
<https://github.com/marcthurley/sharpSAT.git>`__ .

.. code:: shell-session

    $ sharpSAT data/f.cnf
    (The first part omited)
    # solutions 
    48
    # END
    
    time: 0.108726s

The number of solutions can be approximately counted by `ApproxMC <https://github.com/meelgroup/approxmc>`__ .

.. code:: python

    import pyapproxmc
    c = pyapproxmc.Counter()
    for i in range(mgr.get_ncls()):
        c.add_clause(list(mgr.get_clause(i)))
    count = c.count()
    print("Approximate count is: %d*2**%d" % (count[0], count[1]))

The output is as follows.

.. code:: shell-session

    Approximate count is: 48*2**0

Sampling Solutions of First-Order Expressible Property
------------------------------------------------------

In the following code block, which uses ``mgr`` created in the previous code block, 
a solution satisfying the current first-order formula ``f``, i.e. a vertex assignment to first-order
variables ``x1``, ``x2``, and ``x3``, can be randomly sampled with ``unigen``, 
`UniGen approximately uniform sampler <https://github.com/meelgroup/unigen>`__ .
The ``pygplib`` in itself does not provide any functionality of 
solving encoded formulas, and is independent of ``unigen`` module.
Please see `the instruction page <https://github.com/meelgroup/unigen>`__ 
for the installation of ``unigen``.

.. code:: python

    from pyunigen import Sampler

    num = 5 # target number of samples

    c = Sampler()
    for i in range(mgr.get_ncls()):
        c.add_clause(list(mgr.get_clause(i)))

    cells, hashes, samples = c.sample(num)
    for ext_assign in samples:
        int_assign = mgr.decode_assignment(ext_assign) # internal CNF vars.
        fo_assign = Fog.st.decode_assignment(int_assign) # first-order vars.
        ans = [Fog.st.object_to_vertex(fo_assign[key]) \
                                    for key in fo_assign.keys()]
        print(ans)

The output is as follows.

.. code:: shell-session

    [4, 5, 3]
    [1, 4, 5]
    [1, 5, 6]
    [4, 1, 5]
    [4, 3, 5]

Solution sampling with `walksat <https://gitlab.com/HenryKautz/Walksat>`__ is as follows:

.. code:: shell-session

    $ echo $(cat data/f.cnf | grep -v ^c) | walksat -numsol 5

Solving Reconfiguration Problems of First-Order Property
--------------------------------------------------------

``examples/recon.py`` computes reconfiguration problems of vertex sets
expressible with first-order formulas. A set of first-order formulas by
which a reconfiguration problem instance is defined is supposed to be
given in formula-file.
This program uses ``pysat`` to compute a solution.
Please see `the instruction page <https://pysathq.github.io/installation/>`__ 
for the installation of ``pysat``.

.. code:: shell-session

   $ python examples/recon.py -t TJ -e "edge" data/sample.col data/sample1.phi
   c SATISFIABLE
   a 3 4 5
   a 1 4 5
   a 1 4 6
   a 1 7 6
   a 2 7 6
   c compile_time  0.1260545253753662
   c solve_time    0.001790761947631836
   c whole_time    0.46629762649536133

.. code:: shell-session

   $ cat data/sample1.phi
   s (~ x1=x2 & ~ edg(x1,x2)) & (~ x1=x3 & ~ edg(x1,x3)) & (~ x2=x3 & ~ edg(x2,x3))
   i x1=V3 & x2=V4 & x3=V5
   f x1=V2 & x2=V7 & x3=V6

The lines starting with ``s``, ``i``, and ``f`` specify a property each
state must satisfy, a property of the initial state, and a property of
the final state, respectively. In stead of specifying transition
relation between states in formula-file, we specified ``-t TJ`` in the
command line, which means Token Jumping.

Note that initial/final state property is not equality relation as set.
Indeed, the assignment x1=V7, x2=V2, x3=V6 for the final state is not
satisfying. To avoid this, the following is a useful notation to
indicate set equality relation.

.. code:: shell-session

   $ cat data/sample4.phi
   s (~ x1=x2 & ~ edg(x1,x2)) & (~ x1=x3 & ~ edg(x1,x3)) & (~ x2=x3 & ~ edg(x2,x3))
   i 3 4 5
   f 2 7 6

The final state constraint ``f 2 7 6`` is equivalent to the following
formula.

::

   (x1=V2 | x1=V7 | x1=V6) & (x2=V2 | x2=V7 | x2=V6) & 
   (x3=V2 | x3=V7 | x3=V6) & (x1=V2 | x2=V2 | x3=V2) & 
   (x1=V7 | x2=V7 | x3=V7) & (x1=V6 | x2=V6 | x3=V6)

::

   usage: recon.py [-h] [-b BOUND] [-t TRANS] [-e ENCODING] arg1 arg2

   positional arguments:
     arg1                  dimacs graph file
     arg2                  formula file

   optional arguments:
     -h, --help            show this help message and exit
     -b BOUND, --bound BOUND
                           Specify maximum bound
     -t TRANS, --trans TRANS
                           Specify transition relation (TS or TJ)
     -e ENCODING, --encoding ENCODING Specify ENCODING type (edge, clique, direct)

History
=======
TBD

Citation
========

Please cite the following paper if you use ``pygplib``:

::

   Takahisa Toda, Takehiro Ito, Jun Kawahara, Takehide Soh, Akira Suzuki, Junichi Teruyama, Solving Reconfiguration Problems of First-Order Expressible Properties of Graph Vertices with Boolean Satisfiability, The 35th IEEE International Conference on Tools with Artificial Intelligence (ICTAI 2023), accepted.

License
=======

MIT License. See `LICENSE <https://github.com/toda-lab/pygplib/blob/main/LICENSE>`__ .

.. |Test| image:: https://github.com/toda-lab/pygplib/actions/workflows/test.yml/badge.svg
   :target: https://github.com/toda-lab/pygplib/actions/workflows/test.yml

.. |Coverage| image:: https://codecov.io/gh/toda-lab/pygplib/graph/badge.svg?token=WWR54JE3M1
  :target: https://codecov.io/gh/toda-lab/pygplib

.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License
