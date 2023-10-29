Pygplib: Python First-Order Graph Property Library
==================================================

|PyPI Version| |Python Versions| |Test| |Coverage| |License| |Documentation|

Introduction
============

``Pygplib`` (Python First-Order Graph Property Library) is a Python module 
for constructing, manipulating, and encoding graph properties expressible 
with first-order logic of graphs.
It serves as a prototyping tool to tackle with 
various graph related applications.
It provides access to state-of-the-art satisfiability technologies 
without advanced knowledge.
Basic steps to follow are :

- Express a graph property of interest as a first-order formula.
- Set a graph structure, and encode a first-order formula into CNF, 
  a canonical normal form for propositional formulas.
- Apply satisfiability tools to the CNF to compute satisfying
  assignments.
- Decode the result into an assignment of first-order variables.

Documentation
=============

For installation, examples, tutorials, and so on, please see `online documentation <https://pygplib.readthedocs.io/en/latest/>`__ .


Citation
========

Please cite the following paper if you use ``pygplib``:

::

   Takahisa Toda, Takehiro Ito, Jun Kawahara, Takehide Soh, Akira Suzuki, Junichi Teruyama, Solving Reconfiguration Problems of First-Order Expressible Properties of Graph Vertices with Boolean Satisfiability, The 35th IEEE International Conference on Tools with Artificial Intelligence (ICTAI 2023), accepted.

Bugs/Requests/Discussions
=========================

Please report bugs and requests from `GitHub Issues
<https://github.com/toda-lab/pygplib/issues>`__ , and 
ask questions from `GitHub Discussions <https://github.com/toda-lab/pygplib/discussions>`__ .

History
=======
Please see `CHANGES <https://github.com/toda-lab/pygplib/blob/main/CHANGES>`__ .

License
=======

Please see `LICENSE <https://github.com/toda-lab/pygplib/blob/main/LICENSE>`__ .

.. |Test| image:: https://github.com/toda-lab/pygplib/actions/workflows/test.yml/badge.svg
   :target: https://github.com/toda-lab/pygplib/actions/workflows/test.yml

.. |Coverage| image:: https://codecov.io/gh/toda-lab/pygplib/graph/badge.svg?token=WWR54JE3M1
   :target: https://codecov.io/gh/toda-lab/pygplib

.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/pygplib
   :target: https://pypi.org/project/pygplib/
   :alt: PyPI - Python Versions

.. |PyPI Version| image:: https://img.shields.io/pypi/v/pygplib
   :target: https://pypi.org/project/pygplib/
   :alt: PyPI - Version

.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License

.. |Documentation| image:: https://readthedocs.org/projects/pygplib/badge/?version=latest
    :target: https://pygplib.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
