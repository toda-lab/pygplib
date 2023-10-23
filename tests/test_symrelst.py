from pygplib import SymRelSt, NameMgr

def test_init():
    tests = [
        #      1 2 3
        #   1: 1 0 1
        #   3: 0 1 1
        #   2: 1 1 0
        (
            (1,3,2),
            ((1,2), (3,2),(3,1)),
            {
                "code_length" : 3,
                "_codes" : ((1,3),(2,3),(1,2)),
                "_pos" : {1:0,3:1,2:2,(1,3):0,(2,3):1,(1,2):2}
            }
        ),
        #      1 2 3 4
        #   1: 1 0 0 1
        #   4: 0 0 0 0
        #   3: 1 0 0 0 
        #   2: 1 1 0 0
        (
            (1,4,3,2),
            ((1,3,2), (2,),(),(1,)),
            {
                "code_length" : 4,
                "_codes" : ((1,4),(),(1,),(1,2)),
                "_pos" : {1:0,4:1,3:2,2:3,(1,4):0,():1,(1,):2,(1,2):3}
            }
        ),

    ]


    for domain, relation, expected in tests:
        NameMgr.clear()
        max_obj = 4
        universe = set([NameMgr.lookup_index(f"V{i+1}")\
                         for i in range(max_obj)])
        for obj in domain:
            assert obj in universe, \
                f"test case include object {obj} outside universe."

        st = SymRelSt(domain, relation)
        assert st.code_length == expected["code_length"]
        assert st._codes == expected["_codes"]
        assert st._pos == expected["_pos"]
        for pos, obj in enumerate(st.domain):
            assert st._pos_to_object(st._object_to_pos(obj)) == obj
            assert st._object_to_pos(st._pos_to_object(pos)) == pos


def test_get_boolean_var():

    domain = (1,3,2)
    relation = ((1,2), (3,2),(3,1))
    NameMgr.clear()
    max_obj = 4
    universe = set([NameMgr.lookup_index(f"V{i+1}")\
                for i in range(max_obj)])
    for obj in domain:
        assert obj in universe, \
            f"test case include object {obj} outside universe."

    st = SymRelSt(domain, relation)
    for obj in domain:
        name = NameMgr.lookup_name(obj)
        index_list = [NameMgr.lookup_index(f"{name}@{pos+1}") \
                    for pos in range(st.code_length)]
        for pos in range(st.code_length):
            assert st.get_boolean_var(obj, pos) == index_list[pos]

def test_get_symbol_index():

    domain = (1,3,2)
    relation = ((1,2), (3,2),(3,1))
    NameMgr.clear()
    max_obj = 4
    universe = set([NameMgr.lookup_index(f"V{i+1}")\
                for i in range(max_obj)])
    for obj in domain:
        assert obj in universe, \
            f"test case include object {obj} outside universe."

    st = SymRelSt(domain, relation)
    for obj in domain:
        name = NameMgr.lookup_name(obj)
        index_list = [NameMgr.lookup_index(f"{name}@{pos+1}") \
                    for pos in range(st.code_length)]
        for i in index_list:
            assert st.get_symbol_index(i) == obj

def test_get_code_pos():

    domain = (1,3,2)
    relation = ((1,2), (3,2),(3,1))
    NameMgr.clear()
    max_obj = 4
    universe = set([NameMgr.lookup_index(f"V{i+1}")\
                for i in range(max_obj)])
    for obj in domain:
        assert obj in universe, \
            f"test case include object {obj} outside universe."

    st = SymRelSt(domain, relation)
    for obj in domain:
        name = NameMgr.lookup_name(obj)
        index_list = [NameMgr.lookup_index(f"{name}@{pos+1}") \
                    for pos in range(st.code_length)]
        for pos, i in enumerate(index_list):
            assert st.get_code_pos(i) == pos


def test_decode_assignment():

    tests = [
        ("-x@1,x@2", {"V3"}),
        ("x@2,-x@1", {"V3"}),
        ("-x@1,x@2,y@1,y@2", {"V3", "V1"}),
        ("-x@1,y@1,x@2,y@2", {"V3", "V1"}),
        ("-x@1,x@2,-y@1,y@2", {"V3"}),
        ("-x@1,x@2,y@1,y@2,-z@1,-z@2", {"V3", "V1", "V4"}),
        ("-x@1,x@2,y@1,y@2,-z@1,-z@2,w@1,-w@2", {"V3", "V1", "V4", "V2"}),
    ]


    #    | 1 2
    #  --|----
    #  1 | 1 1
    #  2 | 1 0
    #  3 | 0 1
    #  4 | 0 0 
    domain = (1,2,3,4)
    relation = ((1,2), (1,3))
    NameMgr.clear()
    max_obj = 4
    universe = set([NameMgr.lookup_index(f"V{i+1}")\
                for i in range(max_obj)])
    for obj in domain:
        assert obj in universe, \
            f"test case include object {obj} outside universe."
    st = SymRelSt(domain,relation)

    for test_str, expected in tests:
        assign = []
        for name in test_str.split(","):
            sign = 1
            name = name.replace(" ", "")
            if name[0] == "-":
                sign = -1
            name = name.replace("-", "")
            NameMgr.lookup_index(name.split("@")[0])
            index = NameMgr.lookup_index(name)
            assign.append(sign * index)
        res = st.decode_assignment(assign)
        elem_set = set()
        for key in res:
            elem_set.add(NameMgr.lookup_name(res[key]))
        assert elem_set == expected

def test_enc_dec():

    tests = [
        ("x@1", ("x", 1)),
        ("x@2", ("x", 2)),
        ("Va@1", ("Va", 1)),
        ("V1_a@2", ("V1_a", 2)),
    ]

    #    | 1 2
    #  --|----
    #  1 | 1 1
    #  2 | 1 0
    #  3 | 0 1
    #  4 | 0 0 
    domain = (1,2,3,4)
    relation = ((1,2), (1,3))
    NameMgr.clear()
    max_obj = 4
    universe = set([NameMgr.lookup_index(f"V{i+1}")\
                for i in range(max_obj)])
    for obj in domain:
        assert obj in universe, \
            f"test case include object {obj} outside universe."
    st = SymRelSt(domain,relation)

    for test_str, expected in tests:
        NameMgr.lookup_index(test_str.split("@")[0])
        index = NameMgr.lookup_index(test_str)

        assert st.exists_symbol(index)
        res = st.get_symbol_index(index)
        assert NameMgr.lookup_name(res) == expected[0]

        pos = st.get_code_pos(index)
        assert pos + 1 == expected[1]

        assert st.exists_boolean_var(res, pos)
        assert st.get_boolean_var(res, pos) == index
