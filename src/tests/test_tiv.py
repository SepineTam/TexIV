import importlib


def test_texiv_it(monkeypatch):
    texiv_mod = importlib.import_module('texiv.core.texiv')
    t = texiv_mod.TexIV()
    monkeypatch.setattr(t.chunker, 'segment_from_text', lambda x: ['a', 'b', 'c'])
    import numpy as np
    monkeypatch.setattr(t.embedder, 'embed', lambda inp: np.array([[1], [2], [3]]) if len(inp) > 1 else np.array([[1]]))
    monkeypatch.setattr(t.similar, 'similarity', lambda a, b: np.array([[0.6], [0.4], [0.8]]))
    monkeypatch.setattr(t.filter, 'filter', lambda dist: dist >= 0.5)
    monkeypatch.setattr(t.filter, 'two_stage_filter', lambda m: np.array([row[0] for row in m.data]))
    res = t.texiv_it('content', ['kw'])
    assert res == {'freq': 2, 'count': 3, 'rate': 2/3}
