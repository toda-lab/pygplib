
def binary_code(n: int, code_length: int):
    if code_length <= 0 or not 0 <= n < 2**code_length:
        raise ValueError()
    res = []
    while True:
        if n%2 == 0:
            res.append(0)
        else:
            res.append(1)
        if n < 2:
            break
        n = n/2 
    while len(res) < code_length:
        res.append(0)
    assert len(res) == code_length
    return res
