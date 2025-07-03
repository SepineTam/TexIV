import logging
from typing import Callable, Dict, List

import numpy as np
# import ollama
from openai import OpenAI

from ..utils import list2nparray

# _pending_registrations = {}


# def _register(embed_type: str):
#     def decorator(func):
#         _pending_registrations[embed_type] = func
#         return func
#
#     return decorator


class Embed:
    _MAX_LENGTH = 64

    def __init__(self,
                 embed_type: str = None,
                 model: str = None,
                 base_url: str = None,
                 api_key: str = None,
                 max_length: int = None):
        self.embed_type = embed_type
        self.model = model
        if embed_type == "ollama":
            if base_url is None:
                base_url = "https://localhost:11434"
            if api_key is None:
                api_key = "ollama" if api_key is None else api_key
        self.base_url = base_url
        self.api_key = api_key

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        if max_length:
            self._MAX_LENGTH = max_length

    def embed(self, input_text: List[str]) -> np.ndarray:
        length = len(input_text)
        logging.info(f"This Embedding Process has {length} texts to embed.")
        text_batches: List[List[str]] = self._split_text(input_text)
        batch_embeddings = []
        for batch in text_batches:
            batch_result = self._bench_embed(batch)
            batch_embeddings.append(batch_result)

        return np.concatenate(batch_embeddings, axis=0)

    def _bench_embed(self, input_text: List[str]) -> np.ndarray:
        resp = self.client.embeddings.create(
            model=self.model,
            input=input_text
        )
        vectors = [record.embedding for record in resp.data]
        embeddings = list2nparray(vectors)
        return embeddings

    def _split_text(self, input_text: List[str], max_length: int = None) -> List[List[str]]:
        if max_length is None:
            max_length = self._MAX_LENGTH
        if max_length <= 0 or len(input_text) <= max_length:
            return [input_text]
        result = []
        current_chunk = []
        for text in input_text:
            if len(current_chunk) < max_length:
                current_chunk.append(text)
            else:
                result.append(current_chunk)
                current_chunk = [text]

        if current_chunk:
            result.append(current_chunk)

        return result


if __name__ == "__main__":
    embedder = Embed(
        embed_type="openai",
        model="BAAI/bge-m3",
        base_url="https://api.siliconflow.cn/v1",
        api_key="sk-sgokfzyabbzwfylktgwtwionmuexdxgiyzzofmcvdsdvkbqw")
    content = "滚滚长江东逝水，浪花淘尽英雄。我曾经仰望天空，想数清楚天空中的云朵到底在想写什么，可是我终究是无法靠近，无法知道它到底在哪里。"
    embeddings = embedder.embed([content])
    print(embeddings)
    print(type(embeddings))
    print(embeddings.shape)
