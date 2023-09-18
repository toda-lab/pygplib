import pygplib.util as util

def test_parse_dimacs_out():
    tests = (\
        (\
        "v 1 -2 3\n"\
        +"v 4 0\n"\
        +"v -1 2 -3\n"\
        +"v -4 0\n",
        ((1,-2,3,4),(-1,2,-3,-4))\
        ),\
    )

    for test_str, expected in tests:
        assert util.parse_dimacs_out(test_str) == expected

def test_parse_ecc():
    tests = (\
        (\
        "1\n"
        + "\n"
        + "1 3 2\n"\
        + "3 4 5 7\n",\
        ((1,),(1,3,2),(3,4,5,7))\
        ),\
    )

    for test_str, expected in tests:
        assert util.parse_ecc(test_str) == expected

def test_convert_ecc_to_domain():
    tests = (\
        (((1,2,3), (3,4,5)), ((1,),(1,),(1,2),(2,),(2,))),\
        (((1,2,3), (3,4,5),(1,3),(3,4)), ((1,3),(1,),(1,2,3,4),(2,4),(2,))),\
        (((1,2,3), (5,4,3),(3,1),(3,4)), ((1,3),(1,),(1,2,3,4),(2,4),(2,))),\
    )
    
    for test_ecc, expected in tests:
        assert util.convert_ecc_to_domain(test_ecc) == expected


def test_update_domain_by_edge_addition():
    tests = (\
        (((1,2,3), (3,4,5)), \
        ((1,),(1,),(1,2),(2,),(2,)), \
        ((1,),(1,3),(1,2,3,4),(2,),(2,4)), \
        ),\
    )
    
    for test_ecc, test_domain, expected in tests:
        assert util.update_domain_by_edge_addition(test_ecc,test_domain) \
                == expected
