"""Reconfiguration problem solver for first-order properties of graph vertices"""
import os
import time

from argparse import ArgumentParser

from pysat.formula import CNF
from pysat.solvers import Solver

from pygplib import NameMgr, Fo, GrSt
from pygplib import util
from pygplib import op
from bmc     import Bmc


def get_option():
    """Gets command-line options."""
    ap = ArgumentParser()
    ap.add_argument("-b", "--bound", type=int,
                default=10,
                help="Specify maximum bound")
    ap.add_argument("-t", "--trans", type=str,
                default="TJ",
                help="Specify transition relation (TS or TJ)")
    ap.add_argument("-d", "--tmpdir", type=str,
                default="tmp",
                help="Specify temporary directory")
    ap.add_argument("-e", "--ecc", type=str,
                default="edge",
                help="Specify ECC type (edge or clique)")
    ap.add_argument("arg1", help="dimacs graph file")
    ap.add_argument("arg2", help="formula file")

    return ap.parse_args()


def parse_formula_file(file_name: str) -> tuple[str, str, str, str]:
    """Parses formula-file."""
    with open(file_name, "r", encoding="utf-8") as f:
        data = f.read()

    state_str = ""
    trans_str = ""
    ini_str   = ""
    fin_str   = ""
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

    return " & ".join( [n+"="+m  for n, m in zip(variable_name, vertex_name)] )


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
        tmp.append("(" + " | ".join([n+"="+m for m in vertex_name]) + ")")
    # supset relation
    for m in vertex_name:
        tmp.append("(" + " | ".join([n+"="+m for n in variable_name]) + ")")
    return " & ".join(tmp)


start_time  = time.time()
ecc_jar = "ECC8.jar"
tmp_dir = "tmp/"
# NOTE: all data in tmp directory must be deleted before execution.
# Otherwise, ECC8 will recycle past data.

args = get_option()

graph_file   = args.arg1
formula_file = args.arg2
max_bound    = args.bound
trans_type   = args.trans
tmp_dir      = args.tmpdir
ecc_type     = args.ecc

basename  = os.path.splitext(os.path.basename(graph_file))[0]
cover_file= tmp_dir + "/" + basename + ".col-rand.EPSc.cover"
cnf_file  = tmp_dir + "/" + basename + ".cnf"
log_file  = tmp_dir + "/" + basename + ".sover.log"

phi = parse_formula_file(formula_file)
state_expr = Fo.read(phi[0])
trans_expr = Fo.read(phi[1]) if phi[1] != "" else None
name_list  = [NameMgr.lookup_name(v) for v in op.get_free_vars(state_expr)]
ini_expr   = Fo.read(convert_ini_str(phi[2], name_list))
fin_expr   = Fo.read(convert_fin_str(phi[3], name_list))
trans_type = "None" if phi[1] != "" else "TJ"

if ecc_type == "edge":
    ecc = util.compute_ecc_edge(graph_file)
    domain = util.convert_ecc_to_domain(ecc)
elif ecc_type == "clique":
    util.run_ecc8(graph_file, tmp_dir, ecc_jar)
    with open(cover_file, "r", encoding="utf-8") as g:
        _data = g.read()

    ecc = util.parse_ecc(_data)
    domain = util.convert_ecc_to_domain(ecc)
    domain = util.update_domain_by_edge_addition(ecc, domain)
else:
    raise Exception("undefined ECC type")

Fo.st = GrSt(domain)
bmc = Bmc(state_expr, trans_expr, ini_expr, fin_expr, trans_type=trans_type)

solve_time   = 0
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
        res = Fo.st.get_interpretation_of_assign(assign)
        state = [res[key] + 1 for key in sorted(res.keys())]
        ans.append(state)
        print("a " + " ".join(map(str,state)))
    break

if not solved:
    print("c UNSATISFIABLE")

end_time = time.time()
whole_time = end_time - start_time

print(f"c compile_time  {compile_time}")
print(f"c solve_time    {solve_time}")
print(f"c whole_time    {whole_time}")
