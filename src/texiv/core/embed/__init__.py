from typing import Callable, Dict, List

import numpy as np
import ollama
from openai import OpenAI

from ..utils import list2nparray

_pending_registrations = {}


def _register(embed_type: str):
    def decorator(func):
        _pending_registrations[embed_type] = func
        return func

    return decorator


class Embed:
    _embedders: Dict[str, Callable] = {}

    def __init__(self,
                 embed_type: str = None,
                 model: str = None,
                 base_url: str = None,
                 api_key: str = None):
        self.embed_type = embed_type
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

        self._embedders.update(_pending_registrations)

    def embed(self, input_text: List[str]):
        fn = self._embedders[self.embed_type]
        return fn(self, input_text)

    @_register("ollama")
    def _embed_with_ollama(self, input_text: List[str]) -> np.array:
        resp = ollama.embed(model=self.model,
                            input=input_text)
        embeddings = list2nparray(resp.embeddings)
        return embeddings

    @_register("openai")
    def _embed_with_openai(self, input_text: List[str]) -> np.array:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # 发起 embeddings 请求
        resp = client.embeddings.create(
            model=self.model,
            input=input_text
        )
        vectors = [record.embedding for record in resp.data]
        embeddings = list2nparray(vectors)
        return embeddings


if __name__ == "__main__":
    embedder = Embed(
        embed_type="openai",
        model="BAAI/bge-m3",
        base_url="https://api.siliconflow.cn/v1",
        api_key="sk-sgokfzyabbzwfylktgwtwionmuexdxgiyzzofmcvdsdvkbqw")
    content = "滚滚长江东逝水，浪花淘尽英雄。我曾经仰望天空，想数清楚天空中的云朵到底在想写什么，可是我终究是无法靠近，无法知道它到底在哪里。"
    embeddings = embedder.embed(content)
    print(embeddings)
    print(type(embeddings))
    print(embeddings.shape)
