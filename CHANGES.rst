.. _`changes`

CHANGES
=======

Version 2.0.0 - 2023-10-29
--------------------------

Added
^^^^^

- ``BUILDING.rst``, ``CODE_OF_CONDUCT.md``.
- ``pyproject.toml`` to build and package project with poetry.
- ``tox.ini`` and ``.github/*`` for continuous integration.
- rst files and ``requirements.txt`` in ``docs/`` and ``.readthedocs.yaml`` for tutorial documentation in Read the Docs.
- Added ``pygplib/ecc.py`` for insourcing of the edge-clique-cover computation.
- implemented direct-encoding for domain of discource.

Removed
^^^^^^^

- ``tools/``, ``tests/test_solver.py``, ``pygplib/util.py`` and ``tests/test_util.py`` to remove depedencies to third-party tools.

Changed
^^^^^^^

- Changed ``README.md`` to ``README.rst`` and moved tutorial documentation in it to Read the Docs.
- Renamed ``Fo`` class to ``Fog`` class, ``pygplib/fo.py`` to ``pygplib/fog.py``, ``tests/test_fo.py`` to ``tests/test_fog.py``, and ``tests/test_fo_excp.py`` to ``tests/teste_fog_excp.py``.
- Reorganized ``pygplib/st.py`` and divided it to ``pygplib/symrelst.py``, ``pygplib/baserelst.py``, and ``pygplib/be.py`` (added corresponding test files in ``tests/``).
- Updated ``pygplib/grst.py`` so that 

 - ``GrSt`` object is initialized with a vertex-list and a edge-list, and the ECC computation is performed in the initialization.
 - the interpretation of relation symbols ``=`` and ``edg`` as well as ``compute_domain_constraint()`` are included in ``pygplib/gsrt.py``, making ``Fog`` class and ``op.py`` indepedent of domain encoding.
 - the format of first-order formulas (negation, existential and universal quantifiers) to make it compartible with TPTP format.
 - Renamed ``decode_assign()`` of ``pygplib/cnf.py`` to ``decode_assignment()`` and changed an output assignment so that auxiliary variables are ignored.
 - Removed field ``st`` in formula class and changed to give relational structure as argument of each method that requires it. 
 - Changed API of ``compute_domain_constraint()`` so that the input is an index of a free variable and the output is a Prop formula object.
