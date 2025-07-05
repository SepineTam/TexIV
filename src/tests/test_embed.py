import importlib


def test_embed_with_ollama():
    embed_mod = importlib.import_module('texiv.core.embed')
    emb = embed_mod.Embed(embed_type='ollama', model='m')
    vec = emb.embed(['a', 'b'])
    assert vec.shape == (2, 3)


def test_embed_with_openai():
    embed_mod = importlib.import_module('texiv.core.embed')
    emb = embed_mod.Embed(embed_type='openai', model='m', base_url='x', api_key='y')
    vec = emb.embed(['x'])
    assert vec.shape == (1, 3)
