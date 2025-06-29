import numpy as np


def test_list2nparray():
    from texiv.core.utils import list2nparray
    data = [[1, 2], [3, 4]]
    arr = list2nparray(data)
    assert arr.shape == (2, 2)
    assert arr.data == [[1.0, 2.0], [3.0, 4.0]]
