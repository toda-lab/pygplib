import random

from pygplib import Prop, Fog, NameMgr
import pygplib.op as op

class AbsExprPool:
    def __init__(self):
        self.pool = list()

    def add(self, f) -> None:
        if f not in self.pool:
            self.pool.append(f)

    def choice(self, minsize = 1, maxsize = None):
        #return random.choice(self.pool)
        li = list(filter(lambda f: maxsize is None or minsize <= op.compute_size(f) <= maxsize, self.pool))
        return random.choice(li)

    def _mutate(self, maxsize = None) -> None:
        pass

    def mutate(self, n: int = 1, maxsize = None) -> None:
        for i in range(n):
            self._mutate(maxsize=maxsize)

class PropPool(AbsExprPool):
    def __init__(self, tags: tuple[str] = Prop._BINOP_TAGS + Prop._UNOP_TAGS):
        self.tags = tuple(tags)
        super().__init__()

    def _mutate(self, maxsize = None) -> None:
        tag = random.choice(self.tags)
        if tag in Prop._UNOP_TAGS:
            f = self.choice(maxsize=maxsize)
            res = Prop.neg(f)
        elif tag in Prop._BINOP_TAGS:
            f = self.choice(maxsize=maxsize)
            g = self.choice(maxsize=maxsize)
            res = Prop.binop(tag, f, g)
        else:
            raise Exception(f"unknown tag: {tag}")
        self.add(res)

class FogPool(AbsExprPool):
    def __init__(self, tags: tuple[str] = Fog._QF_TAGS + Fog._BINOP_TAGS + Fog._UNOP_TAGS):
        self.tags = tuple(tags)
        super().__init__()

    def _mutate(self, maxsize = None) -> None:
        tag = random.choice(self.tags)
        if tag in Fog._UNOP_TAGS:
            f = self.choice(maxsize=maxsize)
            res = Fog.neg(f)
        elif tag in Fog._BINOP_TAGS:
            f = self.choice(maxsize=maxsize)
            g = self.choice(maxsize=maxsize)
            res = Fog.binop(tag, f, g)
        elif tag in Fog._QF_TAGS:
            f = self.choice(maxsize=maxsize)
            tup = type(self).get_vars(f)
            if len(tup) > 0:
                x in random.choice(tup)
                res = Fog.qf(tag, f, x)
            else:
                res = None
        else:
            raise Exception(f"unknown tag: {tag}")
        if res is not None:
            self.add(res)

    @staticmethod
    def get_vars(f: Fog):
        res = set()
        for i, g in generate_subformulas(f):
            if i == 0:
                if Fog.is_edg_atom(g)\
                    or Fog.is_eq_atom(g):
                    for i in [1,2]:
                        v = g.get_atom_arg(i)
                        if NameMgr.is_variable(v):
                            res.add(v)
                continue
        return tuple(res)
