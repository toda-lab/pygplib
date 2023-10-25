.. _First-OrderLogicGraphs:

First-Order Logic of Graphs
===========================

- An *atomic formula* has one of the forms: ``x = y``, ``edg(x,y)``, ``T`` or ``F``, where ``x``, ``y`` are variables or constants. 
- Given a graph ``G``, *variables* range over the vertices in ``G`` and *constants* are associated with the vertices of ``G``. 
- Vertices are identified with the associated constants. 
- The relation symbol ``edg`` is interpreted as the adjacency relation between vertices in ``G``, the symbol ``=`` as the identity relation over the vertices of ``G``, and ``T`` and ``F`` as true and false, respectively. 
- There is no function and no relation symbol other than ``edg``, ``=``, ``T`` and ``F``. 
- A *first-order formula* is constructed from atomic formulas by using operations such as AND,OR,NOT, logical implication, logical equivalence options, and universal/existential quantifiers.
