from pygplib import NameMgr


def test_name_mgr():
    test_names = [
        ("x12", True),
        ("y", True),
        ("V1", False),
        ("k2", True),
        ("x1", True),
        ("x2", True),
        ("x3", True),
        ("y2@1", True),
        ("V2", False),
        ("V3", False),
        ("y1", True),
        ("x_1", True),
        ("X_1_x@2", False),
    ]

    NameMgr.clear()

    index_list = []
    for name, is_var in test_names:
        assert not NameMgr.has_index(name)
        new_index = NameMgr.lookup_index(name)
        assert NameMgr.has_index(name)
        index_list.append(new_index)

        assert NameMgr.is_variable(new_index) == is_var
        assert NameMgr.is_constant(new_index) != is_var

    for index in index_list:
        assert index > 0
        assert NameMgr.has_name(index)

    for name, is_var in test_names:
        index = NameMgr.lookup_index(name)
        res = NameMgr.lookup_name(index)
        assert res == name, f"{res}, {name}"

    for index in index_list:
        name = NameMgr.lookup_name(index)
        res = NameMgr.lookup_index(name)
        assert res == index, f"{res}, {index}"
