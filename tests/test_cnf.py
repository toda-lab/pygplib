from pygplib import Cnf, Prop, NameMgr, op


def test_cnf_mgr():
    tests = [
        "T",
        "F",
        "x@1",
        "~ x@1",
        "x@1 & x@2",
        "x@1 | x@2",
        "x@1 -> x@2",
        "x@1 <-> x@2",
        "x@1 <-> x@2 & x@3",
        "T | ~ x@1 <-> x@2 & x@3",
    ]
    NameMgr.clear()

    for test_str in tests:
        res = Prop.read(test_str)
        base, naux, cnf1 = op.compute_cnf((res,))

        if cnf1 == ():
            cnf_set1 = set()
        elif cnf1 == ((),):
            cnf_set1 = {""}
        else:
            cnf_set1 = {",".join(map(str, sorted(cls))) for cls in cnf1}

        mgr = Cnf((res,))
        assert mgr.get_ncls() == len(cnf1)

        cnf_set2 = set()
        for pos in range(mgr.get_ncls()):
            cls = map(mgr.decode_lit, mgr.get_clause(pos))
            cls_str = ",".join(map(str, sorted(cls)))
            cnf_set2.add(cls_str)

        assert cnf_set1 == cnf_set2

        max_var = 0
        for pos in range(mgr.get_ncls()):
            if len(mgr.get_clause(pos)) == 0:
                continue
            val = max(mgr.get_clause(pos))
            max_var = val if max_var < val else max_var

        assert mgr.get_nvar() == max_var
