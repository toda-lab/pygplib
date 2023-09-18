from pygplib import GrSt, NameMgr, Fo
import pygplib.op as op

def test_init():
    tests = [
        (((1,2),(1,)), (2, 2,("11","10"))),
        (((),(1,)), (2, 1, ("0","1"))),
        (((1,2,3),(1,),(2,3),(3,)), (4, 3, ("111", "100", "011", "001"))),
    ]

    NameMgr.clear()

    for domain, expected in tests:

        st = GrSt(domain)
        assert st._N == expected[0]
        assert st._M == expected[1]

        assert st._N == len(st._D)

        for code in st._D:
            assert len(code) == st._M
            for val in code:
                assert val == 0 or val == 1

        tab = [0]*st._N
        for code in st._D:
            key = tuple(sorted([i for i, v in enumerate(code) if v == 1]))
            assert key in st._invdict
            tab[st._invdict[key]] = 1

        for i in range(st._N):
            assert tab[i] == 1

        tup = st.get_constant_symbol_tuple()
        for i in range(st._N):
            name = st._prefix + f"{i+1}"
            assert NameMgr.lookup_index(name) == tup[i]

        assert len(st._V) == st._N
        assert len(set(st._V)) == st._N

        for i in range(st._N):
            code = st.get_code(tup[i])
            assert "".join(map(str,code)) == expected[2][i]

    st = GrSt(((),(1,)), prefix="VRT")
    Fo.st = st
    tup = st.get_constant_symbol_tuple()
    form = Fo.edg(tup[0], tup[1])
    res_str=op.to_str(form)
    assert res_str == "edg(VRT1, VRT2)"

def test_enc_dec():
    tests = [
        ("x@1", ("x", 1)),
        ("x@2", ("x", 2)),
        ("Va@12", ("Va", 12)),
        ("V1_a@21", ("V1_a", 21)),
    ]

    NameMgr.clear()

    domain = ((1,2),(1,),(12,22))
    st = GrSt(domain)

    for test_str, expected in tests:
        NameMgr.lookup_index(test_str.split("@")[0])
        index = NameMgr.lookup_index(test_str)

        assert st.exists_symbol(index)
        res = st.get_symbol_index(index)
        assert NameMgr.lookup_name(res) == expected[0]

        pos = st.get_code_pos(index)
        assert pos+1 == expected[1]

        assert st.exists_prop_var(res, pos)
        assert st.get_prop_var(res,pos) == index

def test_get_interpretation_of_assign():
    tests = [
        ("-x@1,x@2", {"01"}), 
        ("x@2,-x@1", {"01"}), 
        ("-x@1,x@2,y@1,y@2", {"01","11"}), 
        ("-x@1,y@1,x@2,y@2", {"01","11"}), 
        ("-x@1,x@2,-y@1,y@2", {"01"}), 
        ("-x@1,x@2,y@1,y@2,-z@1,-z@2", {"01","11","00"}), 
        ("-x@1,x@2,y@1,y@2,-z@1,-z@2,w@1,-w@2", {"01","11","00","10"}), 
    ]

    NameMgr.clear()

    domain = ((1,2),(1,),(2,),())
    st = GrSt(domain)
    const_tup = st.get_constant_symbol_tuple()

    for test_str, expected in tests:
        assign = []
        for name in test_str.split(","):
            sign = 1
            name = name.replace(" ", "")
            if name[0] == "-":
                sign = -1
            name = name.replace("-","")
            NameMgr.lookup_index(name.split("@")[0])
            index = NameMgr.lookup_index(name)
            assign.append(sign * index)
        res = st.get_interpretation_of_assign(assign)
        elem_set = set()
        for key in res:
            elem_index = const_tup[res[key]]
            code = st.get_code(elem_index)
            elem_set.add("".join(map(str, code)))
        assert elem_set == expected

