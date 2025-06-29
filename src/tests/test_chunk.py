import importlib


def test_segment_from_text():
    chunk_module = importlib.import_module('texiv.core.chunk')
    chunker = chunk_module.Chunk(stopwords={'我', '天安门'})
    tokens = chunker.segment_from_text('我 爱 北京 天安门')
    assert tokens == ['爱', '北京']


def test_load_stopwords_file(tmp_path):
    chunk_module = importlib.import_module('texiv.core.chunk')
    stop = tmp_path / 'stop.txt'
    stop.write_text('我')
    chunker = chunk_module.Chunk()
    chunker.load_stopwords_file(str(stop))
    assert chunker.segment_from_text('我 爱 你') == ['爱', '你']
