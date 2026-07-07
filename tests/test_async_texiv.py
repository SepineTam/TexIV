import asyncio

import numpy as np
import pandas as pd
import pytest

import texiv.core.texiv as texiv_module
from texiv import AsyncTexIV, set_parallel_count
from texiv.utils import create_rich_helper


@pytest.fixture(autouse=True)
def reset_parallel_count():
    original_parallel_count = texiv_module._parallel_count
    yield
    texiv_module._parallel_count = original_parallel_count


class FakeEmbedder:
    async def async_embed(self, input_text):
        await asyncio.sleep(0)
        vectors = []
        for text in input_text:
            if text == "alpha":
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return np.array(vectors)


def build_async_texiv():
    texiv = AsyncTexIV(valve=0.5, rich_helper=create_rich_helper(quiet=True))
    texiv.embedder = FakeEmbedder()
    texiv.chunker.segment_from_text = lambda text: text.split()
    return texiv


def test_set_parallel_count_controls_new_async_instances():
    set_parallel_count(10)

    texiv = AsyncTexIV(rich_helper=create_rich_helper(quiet=True))

    assert texiv.IS_ASYNC is True
    assert texiv.max_concurrency == 10
    assert texiv.embedder._max_concurrency == 10


def test_set_parallel_count_rejects_invalid_values():
    with pytest.raises(ValueError):
        set_parallel_count(0)


def test_async_texiv_it_returns_description():
    texiv = build_async_texiv()

    result = asyncio.run(texiv.texiv_it("alpha beta", ["alpha"]))

    assert result == {"freq": 1, "count": 2, "rate": 0.5}


def test_async_texiv_df_writes_result_columns():
    texiv = build_async_texiv()
    df = pd.DataFrame({"text": ["alpha beta", "beta"]})

    result = asyncio.run(texiv.texiv_df(df, "text", "alpha"))

    assert result["text_freq"].tolist() == [1, 0]
    assert result["text_count"].tolist() == [2, 1]
    assert result["text_rate"].tolist() == [0.5, 0.0]
