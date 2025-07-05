import importlib


def test_filter_value():
    filt_mod = importlib.import_module('texiv.core.filter')
    f = filt_mod.Filter(valve=0.5)
    import numpy as np
    data = np.array([[0.4, 0.6], [0.8, 0.2]])
    result = f.filter(data, valve=0.6)
    assert result.data == [[0.0, 1.0], [1.0, 0.0]]


def test_filter_array():
    filt_mod = importlib.import_module('texiv.core.filter')
    f = filt_mod.Filter(VALVE_TYPE='array')
    import numpy as np
    data = np.array([[0.4, 0.6], [0.7, 0.8]])
    valve = np.array([[0.5, 0.5], [0.8, 0.6]])
    result = f.filter(data, valve_array=valve)
    assert result.data == [[0.0, 1.0], [0.0, 1.0]]


def test_two_stage_methods():
    filt_mod = importlib.import_module('texiv.core.filter')
    import numpy as np
    matrix = np.array([[True, False], [True, True], [False, False]])
    f = filt_mod.Filter()
    assert f.row_any_true(matrix).data == [1.0, 1.0, 0.0]
    assert f.row_all_true(matrix).data == [0.0, 1.0, 0.0]
    maj = f.row_majority_true(np.array([[True, False, False], [True, True, False], [False, False, False]]))
    assert maj.data == [0.0, 1.0, 0.0]
