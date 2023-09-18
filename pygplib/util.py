"""Module providing utility functions"""
import os
import sys
import subprocess

from functools import reduce


def parse_dimacs_out(out: str) -> tuple[tuple[int, ...], ...]:
    """Parses solver output in DIMACS CNF format.

    This method can handle solver output in solution enumeration mode.

    Input
    v 1 -2 3
    v 4 0
    v -1 2 -3
    v -4 0

    Output
    ((1,-2,3,4),(-1,2,-3,-4))

    Returns:
        tuple of tuples of nonzero integers, which represents one or more
        solutions (i.e. satisfying assignments).
    """
    res= []
    filtered = "".join([line for line in out.split("\n") if line[:2] == "v "])

    for sol in filtered.replace("v","").split(" 0"):
        if sol == "":
            continue
        assign = [int(x) for x in sol.split(" ") if x != ""]
        if len(assign) == 0:
            raise Exception("Parse failure")
        res.append(tuple(assign))
    return tuple(res)


def parse_ecc(out: str) -> tuple[tuple[int, ...], ...]:
    """Parses ECC (Edge Clique Cover) of output of ECC8.

    ECC file represents an edge clique cover, a collection of cliques such that
    every edge is included in some clique in the collection.
    Each line of ECC file consists of nonzero positive integers, ordered in
    arbitrary order, separated by white space.
    Each such integer represents a vertex, and the vertices of the same line
    represents a clique.

    Graph
    V1 --- V2
     \\    /
      \\  /
       V3
      /  \\
     /    \\
    V4 --- V5

    Input
    1 2 3  // {V1,V2,V3}
    3 4 5  // {V3,V4,V5}

    Output
    ((1,2,3), (3,4,5))

    Note:
        Empty lines are ignored.

    Returns:
        tuple of tuples of nonzero integers with each tuple representing a
        clique.
    """
    ecc = []
    for line in out.split("\n"):
        if len(line) == 0:
            continue
        cliq = [int(x) for x in line.split(" ") if x.isdigit()]
        if len(cliq) == 0:
            raise Exception("Parse failure")
        ecc.append(tuple(cliq))
    return tuple(ecc)


def convert_ecc_to_domain(ecc: tuple) -> tuple[tuple[int, ...], ...]:
    """Converts ECC to domain of first-order variable.

    Domain of first-order variable consists of binary codes, representing
    vertices of a graph.
    Each such binary code represents incidence relation of the vertex, v, of
    the code and cliques, Q, of ECC in such a way that
    v is incident to Q if and only if the code of v has value 1 at position i,
    where i (0<i<=|ECC|) denotes the index of Q.

    Graph
    V1 --- V2
     \\    /
      \\  /
       V3
      /  \\
     /    \\
    V4 --- V5

    Input-1
    ((1,2,3), (3,4,5))

    Output-1
    ((1,),(1,),(1,2),(2,),(2,))

    Input-2
    ((1,2,3), (3,4,5),(1,3),(3,4))

    Output-2
    ((1,3),(1,),(1,2,3,4),(2,4),(2,))

    Returns:
        tuple of tuples of nonzero integers with each tuple meaning a vertex.
        Each such vertex is represented by a collection of cliques to which
        the vertex is incident, in other words, a set of position indices
        such that the binary code of the vertex has value 1.

    Note:
        In binary coding of ECC, different vertices might have the same code
        (see input-1 and output-1),
        which means that such vertices are always determined to be equal to
        each other, even though they are different. A simple solution to avoid
        this is to add more edges to ECC so as to make different vertices
        have different codes (see input-2 and output-2).
    """
    N = max([max(cliq) for cliq in ecc])
    domain = [set() for i in range(N)]
    for i, cliq in enumerate(ecc):
        for j in cliq:
            domain[j-1].add(i+1)
    return tuple([tuple(sorted(s)) for s in domain])


def update_domain_by_edge_addition(ecc: tuple, \
    domain: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    """Update domain by adding more edges so that different vertices have
    different codes.

    See convert_ecc_to_domain for details.

    Returns:
        Updated domain, a tuple of tuples of nonzero positive integers.
    """
    #neghbor[v] is neigborhood of vartex v (1 <= v <= len(domain))
    neighbor = {}
    for pos,code in enumerate(domain):
        v = pos+1
        set_list = [set(ecc[i-1]) for i in code]
        neighbor[v] = reduce(lambda x,y: x.union(y),set_list,set())
        neighbor[v].remove(v)

    # maximum index of clique in ECC
    max_index = len(ecc)

    dic     = {} # dic[key]   = vertex of that code
    inv_dic = {} # inv_dic[v] = latest code of v
    for v in range(1,len(domain)+1):
        latest_code = inv_dic[v] if v in inv_dic else domain[v-1]
        key = tuple(sorted(latest_code))
        if key not in dic:
            dic[key] = v
            assert v not in inv_dic
            inv_dic[v] = latest_code

        else:
            w = dic[key] # v and w have common code
            if v == w:
                continue

            # Find new edge (u,uu) that separates v and w
            diff_set = neighbor[v] - {w}
            if len(diff_set) > 0:
                u = tuple(diff_set)[0]
                uu = v
            else:
                diff_set = neighbor[w] - {v}
                if len(diff_set) == 0:
                    raise Exception(f"isolated edge ({v},{w}) found")
                u = tuple(diff_set)[0]
                assert u != v
                uu = w
            max_index += 1 #index of edge (u,uu)

            # Update u's code
            old_code = inv_dic[u] if u in inv_dic else domain[u-1]
            old_key = tuple(sorted(old_code))
            if old_key in dic:
                dic.pop(old_key)
            new_code = old_code + (max_index,)
            new_key = tuple(sorted(new_code))
            assert new_key not in dic
            dic[new_key] = u
            inv_dic[u] = new_code

            # Update uu's code
            old_code = inv_dic[uu] if uu in inv_dic else domain[uu-1]
            old_key = tuple(sorted(old_code))
            if old_key in dic:
                dic.pop(old_key)
            new_code = old_code + (max_index,)
            new_key = tuple(sorted(new_code))
            assert new_key not in dic
            dic[new_key] = uu
            inv_dic[uu] = new_code

    res = tuple([tuple(sorted(inv_dic[v])) for v in range(1,len(domain)+1)])
    return res


def compute_ecc_edge(filename: str) -> tuple[tuple[int, ...], ...]:
    """Computes ECC of all edges.

    Returns:
        tuple of pairs of nonzero positive integers with each pair representing
        an edge.
    """
    data = ""
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()

    res = []
    for line in data.split("\n"):
        if len(line) == 0:
            continue
        if line[0] == "e":
            v = int(line.split(" ")[1])
            w = int(line.split(" ")[2])
            if v == w:
                raise Exception(f"loop ({v},{w}) found")
            if w < v:
                tmp = v
                v   = w
                w   = tmp
            assert v < w
            res.append( (v, w) )
    return tuple(res)


def run_ecc8(graph_file: str, tmp_dir: str, ecc_jar: str ="ECC/ECC8.jar") \
    -> None:
    """Runs ECC8.

    ECC file and other files of ECC8 are generated into temporary directory.
    The name of ECC file has extension ".col-rand.EPSc.cover".

    Graph
    V1 --- V2
     \\    /
      \\  /
       V3
      /  \\
     /    \\
    V4 --- V5

    Example
    $ ls
    tmp/ ECC8.jar data/ pygplib/ (and other files)
    $ cat data/graph.col
    $ python
    > import pygplib.util as util
    > util.run_ecc8("data/graph.col", tmp_dir="tmp", ecc_jar="ECC8.jar")
    > quit()
    $ ls tmp
    graph.col-rand.EPSc-clq.csv  graph.col-rand.EPSc-nci.csv
    graph.col-rand.EPSc-eci.csv  graph.col-rand.EPSc-stats.txt
    graph.col-rand.EPSc.cover
    $ cat tmp/graph.col-rand.EPSc.cover
    3 1 2
    5 3 4

    Args:
        graph_file: DIMACS graph file
        tmp_dir: temporary directory to which output files are generated.
        ecc_jar: path to ECC8.jar
    """
    if not os.path.isfile(graph_file):
        raise Exception("Cannot find: "+graph_file)
    if not os.path.isdir(tmp_dir):
        raise Exception("Cannot find: "+tmp_dir)
    if not os.path.isfile(ecc_jar):
        raise Exception("Cannot find: "+ecc_jar)
    try:
        subprocess.run(\
            [f"java -jar {ecc_jar} -g {graph_file} -o {tmp_dir} -f dimacs"], \
            shell=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError:
        print("Failed to execute", file=sys.stderr)


def compute_width_of_integer(n: int) -> int:
    """Computes width of integer."""
    if n < 0:
        raise Exception("Set positive number")

    width = 1
    tmp = n
    while tmp >= 10:
        width += 1
        tmp = int(tmp/10)

    return width
