import pytest

from pygplib import GrSt, NameMgr

def test_init():
    NameMgr.clear()
    with pytest.raises(ValueError):
        st = GrSt(((),(1,)),prefix="xV")
    with pytest.raises(ValueError):
        st = GrSt(((),(1,)),prefix="_V")
    with pytest.raises(ValueError):
        st = GrSt(((),(1,)),prefix="1V")
    
def test_get_interpretation_of_assign():
    tests = [
        "-x@1,x@2,y@1,y@2",  # NG: 11
        "-x@1,y@1,-y@1",     # NG: 00
        "-y@1,-y@2",         # NG: 00
    ]

    NameMgr.clear()

    domain = ((1,),(2,)) # 01, 10
    st = GrSt(domain)

    for test_str in tests:
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
        with pytest.raises(Exception):
            st.get_interpretation_of_assign(assign)

def test_get_prop_var():
    NameMgr.clear()

    domain = ((1,),(2,)) # 01, 10
    st = GrSt(domain)
    with pytest.raises(ValueError):
        st.get_prop_var(0,0)

    index = NameMgr.lookup_index("x@1")
    with pytest.raises(Exception):
        st.get_prop_var(index,0)

    index = NameMgr.lookup_index("x")
    with pytest.raises(Exception):
        st.get_prop_var(index,-1)
    with pytest.raises(Exception):
        st.get_prop_var(index,st.get_code_size())

