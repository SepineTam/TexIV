import importlib


def test_cosine_similarity():
    sim_mod = importlib.import_module('texiv.core.similarity')
    sim = sim_mod.Similarity('cosine')
    import numpy as np
    a = np.array([[1, 0], [0, 1]])
    b = np.array([[1, 0], [0, 1]])
    matrix = sim.similarity(a, b)
    assert matrix.data == [[1.0, 0.0], [0.0, 1.0]]
