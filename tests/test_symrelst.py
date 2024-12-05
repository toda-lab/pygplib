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


def test_boolean_encoding():

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
    var_set = {NameMgr.lookup_index(name) for name in ["x", "y", "z"]}
    boolean_var_set = set()
    for i in var_set:
        for pos in range(st.code_length):
            v = st.get_boolean_var(i, pos)
            assert (i,pos) == st.get_variable_position_pair(v)
            boolean_var_set.add(v)
    assert len(boolean_var_set) == len(var_set)*st.code_length

def test_decode_assignment():

    tests = [
        (lambda x,y,z,w: f"-{x[1]},{x[2]}", {"V3"}),
        (lambda x,y,z,w: f"{x[2]},-{x[1]}", {"V3"}),
        (lambda x,y,z,w: f"-{x[1]},{x[2]},{y[1]},{y[2]}", {"V3", "V1"}),
        (lambda x,y,z,w: f"-{x[1]},{y[1]},{x[2]},{y[2]}", {"V3", "V1"}),
        (lambda x,y,z,w: f"-{x[1]},{x[2]},-{y[1]},{y[2]}", {"V3"}),
        (lambda x,y,z,w: f"-{x[1]},{x[2]},{y[1]},{y[2]},-{z[1]},-{z[2]}", {"V3", "V1", "V4"}),
        (lambda x,y,z,w: f"-{x[1]},{x[2]},{y[1]},{y[2]},-{z[1]},-{z[2]},{w[1]},-{w[2]}", {"V3", "V1", "V4", "V2"}),
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
    index_x = NameMgr.lookup_index("x")
    x = [""] + [NameMgr.lookup_name(i) for i in st.get_boolean_var_list(index_x)]
    index_y = NameMgr.lookup_index("y")
    y = [""] + [NameMgr.lookup_name(i) for i in st.get_boolean_var_list(index_y)]
    index_z = NameMgr.lookup_index("z")
    z = [""] + [NameMgr.lookup_name(i) for i in st.get_boolean_var_list(index_z)]
    index_w = NameMgr.lookup_index("w")
    w = [""] + [NameMgr.lookup_name(i) for i in st.get_boolean_var_list(index_w)]
    index_dict = {}
    for i in st.get_boolean_var_list(index_x)\
        + st.get_boolean_var_list(index_y)\
        + st.get_boolean_var_list(index_z)\
        + st.get_boolean_var_list(index_w):
        index_dict[NameMgr.lookup_name(i)] = i

    for func, expected in tests:
        assign = []
        test_str = func(x,y,z,w)
        for name in test_str.split(","):
            name = name.strip()
            if len(name) == 0:
                continue
            if name[0] == "-":
                assign.append( -1 * index_dict[name[1:]] )
            else:
                assign.append( index_dict[name]  )
        res = st.decode_assignment(assign)
        elem_set = {NameMgr.lookup_name(res[key])\
            for key in st.decode_assignment(assign)}
        assert elem_set == expected
