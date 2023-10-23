"""Reconfiguration problem solver for first-order properties of graph vertices"""
import time

from argparse import ArgumentParser
from pysat.formula import CNF
from pysat.solvers import Solver

from pygplib import NameMgr, Fog, GrSt
from pygplib import op
from bmc import Bmc


def get_option():
    """Gets command-line options."""
    ap = ArgumentParser()
    ap.add_argument("-b", "--bound", type=int, default=10, help="Specify maximum bound")
    ap.add_argument(
        "-t",
        "--trans",
        type=str,
        default="TJ",
        help="Specify transition relation (TS or TJ)",
    )
    ap.add_argument(
        "-e",
        "--encoding",
        type=str,
        default="edge",
        help="Specify ECC type (edge, clique, direct)",
    )
    ap.add_argument("arg1", help="dimacs graph file")
    ap.add_argument("arg2", help="formula file")

    return ap.parse_args()

def parse_graph_file(filename: str) -> list[tuple[int, ...], ...]:
    """Computes a graph file in DIMACS format.

    Returns:
        list of pairs of nonzero positive integers with each pair representing
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
                v = w
                w = tmp
            assert v < w
            res.append((v, w))
    return res

def parse_formula_file(file_name: str) -> tuple[str, str, str, str]:
    """Parses formula-file."""
    with open(file_name, "r", encoding="utf-8") as f:
        data = f.read()

    state_str = ""
    trans_str = ""
    ini_str = ""
    fin_str = ""
    for line in data.split("\n"):
        if len(line) == 0:
            continue
        if line[0] == "s":
            state_str = line[1:]
        if line[0] == "t":
            trans_str = line[1:]
        if line[0] == "i":
            ini_str = line[1:]
        if line[0] == "f":
            fin_str = line[1:]
    return (state_str, trans_str, ini_str, fin_str)


def convert_ini_str(formula_str: str, variable_name: list) -> str:
    """Converts initial state formula string if it is a sequence of integers.

    Input (formula_str)
    3 4 5

    Input (variable_name)
    ["x1", "x2", "x3"]

    Output (equality as sequence)
    x1=V3 & x2=V4 & x3=V5
    """
    for x in formula_str.split(" "):
        if len(x) == 0:
            continue
        if not x.isdigit():
            return formula_str
    vertex_name = ["V" + f"{x}" for x in formula_str.split(" ") if len(x) != 0]
    if len(vertex_name) != len(variable_name):
        raise Exception("number of integers in init state is unmatching")

    return " & ".join([n + "=" + m for n, m in zip(variable_name, vertex_name)])


def convert_fin_str(formula_str: str, variable_name: list) -> str:
    """Converts final state formula string if it is a sequence of integers.

    Input (formula_str)
    2 7 6

    Input (variable_name)
    ["x1", "x2", "x3"]

    Output (equality as set)
    (x1=V2 | x1=V7 | x1=V6) & (x2=V2 | x2=V7 | x2=V6) & \
    (x3=V2 | x3=V7 | x3=V6) & (x1=V2 | x2=V2 | x3=V2) & \
    (x1=V7 | x2=V7 | x3=V7) & (x1=V6 | x2=V6 | x3=V6)
    """
    for x in formula_str.split(" "):
        if len(x) == 0:
            continue
        if not x.isdigit():
            return formula_str
    vertex_name = ["V" + f"{x}" for x in formula_str.split(" ") if len(x) != 0]
    if len(vertex_name) != len(variable_name):
        raise Exception("number of integers in fin state is unmatching")

    tmp = []
    # subset relation
    for n in variable_name:
        tmp.append("(" + " | ".join([n + "=" + m for m in vertex_name]) + ")")
    # supset relation
    for m in vertex_name:
        tmp.append("(" + " | ".join([n + "=" + m for n in variable_name]) + ")")
    return " & ".join(tmp)


start_time = time.time()

args = get_option()
graph_file    = args.arg1
formula_file  = args.arg2
max_bound     = args.bound
trans_type    = args.trans
encoding_type = args.encoding

edge_list = parse_graph_file(graph_file)
vertex_list = []
for e in edge_list:
    vertex_list.append(e[0])
    vertex_list.append(e[1])
vertex_list = list(set(vertex_list))

phi = parse_formula_file(formula_file)
state_expr = Fog.read(phi[0])
trans_expr = Fog.read(phi[1]) if phi[1] != "" else None
name_list = [NameMgr.lookup_name(v) for v in op.get_free_vars(state_expr)]
ini_expr = Fog.read(convert_ini_str(phi[2], name_list))
fin_expr = Fog.read(convert_fin_str(phi[3], name_list))
trans_type = "None" if phi[1] != "" else "TJ"

Fog.st = GrSt(vertex_list, edge_list, encoding=encoding_type)
bmc = Bmc(state_expr, trans_expr, ini_expr, fin_expr, trans_type=trans_type)

solve_time = 0
compile_time = 0
solved = False
for step in range(0, max_bound):
    start_compile = time.time()
    bmc.generate_cnf(step)
    end_compile = time.time()
    compile_time += end_compile - start_compile

    cnf = CNF(from_clauses=bmc.cnf)
    with Solver(bootstrap_with=cnf) as solver:
        start_solve = time.time()
        solved = solver.solve()
        end_solve = time.time()
        solve_time += end_solve - start_solve

        if solved:
            model = solver.get_model()
        else:
            continue

    print("c SATISFIABLE")
    ans = []
    for assign in bmc.decode(model):
        res = Fog.st.decode_assignment(assign)
        state = [Fog.st.object_to_vertex(res[key]) for key in res.keys()]
        ans.append(state)
        print("a " + " ".join(map(str, state)))
    break

if not solved:
    print("c UNSATISFIABLE")

end_time = time.time()
whole_time = end_time - start_time

print(f"c compile_time  {compile_time}")
print(f"c solve_time    {solve_time}")
print(f"c whole_time    {whole_time}")
