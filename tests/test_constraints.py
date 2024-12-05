import random
from typing import Iterable

from pygplib import Prop, NameMgr
import pygplib.op as op
import pygplib.constraints as const

from . import solver
from . import tools

def test_at_most_r():
    NameMgr.clear()
    max_n = 100
    x = [NameMgr.lookup_index(f"x{i}") for i in range(1,max_n+1)]
    for step in range(3):
        random.shuffle(x)
        n = 10
        r = random.randint(0,n)
        _test_at_most_r(x[:n], r)

def _test_at_most_r(x: Iterable[int], r: int):
    f = Prop.read(const.at_most_r(x, r))
    code_length = len(x)
    for n in range(2**code_length):
        count = 0
        code = tools.binary_code(n,code_length)
        msg = f"r={r},code="+",".join(map(str,code))
        g = f
        for i, val in enumerate(code):
            if val == 1:
                g = Prop.land(g,Prop.var(x[i]))
                count += 1
            else:
                g = Prop.land(g,Prop.neg(Prop.var(x[i])))
        if count <= r:
            solver.assert_satisfiable(g,msg=msg)
        else:
            solver.assert_unsatisfiable(g,msg=msg)
