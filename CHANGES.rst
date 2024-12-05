.. _`changes`

CHANGES
=======

Version 2.3.0 - 2024-12-05
--------------------------

Fixed
^^^^^

- absexpr.py: constant atoms of different classes (say, true constants of Prop and Fog) were represented as the same objects due to bug in _to_key method of absexpr.py, which are now distinguished by adding class name to key.
- ecc.py: compute_separating_ecc method did not compute separating ecc, which is now corrected and tested.
- cnf.py: all external indices from 1 to self.base are ensured to be decodable.

Changed
^^^^^^^

- absexpr.py: clear method of IndexGen class is changed so as to reset initial index too.
- absprop.py: reduce_formula_step method is changed so as to reduce more by handling cases of implies and iff operators.
- prop.py: syntax of variable accepted by read method is simplified
- fog.py: _normalize_aux method (nomalizing the order of values in aux fields) is changed, depending on atom type (less-than relation, introduced in this release, is not normalized, while the others are normalized same as before).
- ecc.py: simpgraph module is used to handle graph.
- cnf.py: constructor is changed to accept an iterable object.
- cnf.py: encoding to external indices and decoding to internal indices are improved and tested.
- name.py: lookup_index method is changed to fails if names of auxiliary variables introduced by get_aux_index method (see below) are given; if the leading character is "_" and the name is already registered, then this means that it is the index of an auxiliary variable.
- be.py: management of variables introduced in boolean encodings are changed; they are holded in instance variables of be object and managed by be object. Such variables were previosly registered to name manager with variable names seprated by '@', which is now deprecated.
- grst.py: it is improved so as to be extendable and easy to add new encodings.

Added
^^^^^

- fog.py:  atom of form x < y becomes accepted by read method
- name.py: get_aux_index method is added to be able to introduce auxiliary variables in boolean encoding as needed
- be.py: is_decodable_boolean_var method to determine if a boolean variable is decodable into an FO-variable.
- grst.py: new encoding methods (direct, log, and vertex) are implemented.
- op.py: compute_size method to compute formula size.
- constraints.py: encoding of cardinality constraint (at-most-r constraint)

Deprecated
^^^^^^^^^^

- the following methods on the left of ">" have been duplicated and will be remove in version 3.0.0.
    - absexpr.py: is_atom_term     > is_atom
    - absexpr.py: is_unop_term     > is_unop
    - absexpr.py: is_binop_term    > is_binop
    - absneg.py:  is_neg_term      > is_neg
    - absprop.py: is_land_term     > is_land
    - absprop.py: is_lor_term      > is_lor
    - absprop.py: is_implies_term  > is_implies
    - absprop.py: is_iff_term      > is_iff
    - absfo.py:   is_forall_term   > is_forall
    - absfo.py:   is_exists_term   > is_exists
    - absfo.py:   is_qf_term       > is_qf
    - prop.py:    get_atom_value   > (to be deleted)
    - fog.py:     get_atom_value   > get_atom_arg
    - op.py:      generator        > generate_subformulas
    - fog.py:     le               > lt
　  - fog.py:     _LE              > _LT
    - fog.py:     get_le_tag       > get_lt_tag
    - fog.py:     is_le_atom       > is_lt_atom
    - fog.py:     action_le_rel    > action_lt_rel
    - cnf.py:     get_nvar         > (to be deleted)
    - cnf.py:     get_ncls         > (to be deleted)
    - cnf.py:     get_clause       > (to be deleted)
    - cnf.py:     encode_lit       > _encode_lit
    - cnf.py:     decode_lit       > _decode_lit
    - be.py:      get_symbol_index > get_variable_position_pair
    - be.py:      get_code_pos     > get_variable_position_pair
    - be.py:      exists_symbol    > (deleted)
    - be.py:      exists_boolean_var > (deleted)
    - grst.py:    encode_eq        > be_eq
    - grst.py:    encode_edg       > be_edg
    - grst.py:    encode_F         > be_F
    - grst.py:    encode_T         > be_T

Version 2.2.0 - 2024-09-09
--------------------------

Fixed
^^^^^
- recon.py: trans_type could not be changed from default type "TJ".
- recon.py: the strings of init state and final state were incorrectly computed when these
  states are given as sets in a formula file.
- ecc.py: exception unintentially raised when clique encoding is selected and a
  graph includes a vertex of degree 1.


Version 2.1.0 - 2023-11-06
--------------------------

Added
^^^^^

- Made it possible for constructor of Cnf to accept not only tuple but also list as input.


Version 2.0.5 - 2023-11-04
--------------------------

Changed
^^^^^^^

- Update documentation

Version 2.0.4 - 2023-11-04
--------------------------

Deprecated
^^^^^^^^^^

- propnize() and reduce() have been deprecated and will be removed in v3.0.0.


Changed
^^^^^^^

- Renamed propnize() to perform_boolean_encoding().
- Renamed reduce() to reduce_formula().
- Renamed class variable bipartite_order to partitioning_order.

Cleaned
^^^^^^^

- Changed code so that partitioning_order is not accessed outside binop_batch().


Version 2.0.3 - 2023-11-04
--------------------------

Added
^^^^^

- Implemented log-encoding in GrSt class.
- Added tests for log-encoding.

Changed
^^^^^^^

- Changed test_bmc() to validation for all solutions.

Version 2.0.2 - 2023-10-31
--------------------------

Fixed
^^^^^

- Fixed direct-encoding of GrSt class
- Fixed initialization of Ecc object for a graph with isolated vertex (vertex without neighboring vertex).

Changed
^^^^^^^

- Cleaned the code of GrSt class.
- Improved tests for GrSt class.

Version 2.0.1 - 2023-10-29
--------------------------

Added
^^^^^

- Added ``BUILDING.rst`` and ``CODE_OF_CONDUCT.md``.
- Added ``pyproject.toml`` to build and package project with poetry.
- Aded ``tox.ini`` and ``.github/*`` for continuous integration.
- Added rst files and ``requirements.txt`` in ``docs/`` and ``.readthedocs.yaml`` for tutorial documentation in Read the Docs.
- Added ``pygplib/ecc.py`` for insourcing of the edge-clique-cover computation.
- Implemented direct-encoding for domain of discource.

Removed
^^^^^^^

- Removed ``tools/``, ``tests/test_solver.py``, ``pygplib/util.py`` and ``tests/test_util.py`` to remove depedencies to third-party tools.

Changed
^^^^^^^

- Changed ``README.md`` to ``README.rst`` and moved tutorial documentation in it to Read the Docs.
- Renamed ``Fo`` class to ``Fog`` class, ``pygplib/fo.py`` to ``pygplib/fog.py``, ``tests/test_fo.py`` to ``tests/test_fog.py``, and ``tests/test_fo_excp.py`` to ``tests/teste_fog_excp.py``.
- Reorganized ``pygplib/st.py`` and divided it to ``pygplib/symrelst.py``, ``pygplib/baserelst.py``, and ``pygplib/be.py`` (added corresponding test files in ``tests/``).
- Updated ``pygplib/grst.py`` so that 

 - ``GrSt`` object is initialized with a vertex-list and a edge-list, and the ECC computation is performed in the initialization.
 - the interpretation of relation symbols ``=`` and ``edg`` as well as ``compute_domain_constraint()`` are included in ``pygplib/gsrt.py``, making ``Fog`` class and ``op.py`` indepedent of domain encoding.

- Changed the format of first-order formulas (negation, existential and universal quantifiers) to make it compartible with TPTP format.
- Renamed ``decode_assign()`` of ``pygplib/cnf.py`` to ``decode_assignment()`` and changed an output assignment so that auxiliary variables are ignored.
- Renamed ``get_interpretation_of_assign()`` of ``GrSt`` to ``decode_assignment()`` and changed an output assignment so that first-order variables' indices are associated with constant symbol indices. 
- Removed field ``st`` in formula class and changed to give relational structure as argument of each method that requires it. 
- Changed API of ``compute_domain_constraint()`` so that the input is an index of a free variable and the output is a Prop formula object.
