#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

import asyncio
import logging
import time
from typing import List, Union

import numpy as np
from openai import AsyncOpenAI, OpenAI

from ..utils import list2nparray


# TODO: 修改异步逻辑
class Embed:
    _MAX_LENGTH = 64
    retry_times = 3

    def __init__(self,
                 embed_type: str = None,
                 model: str = None,
                 base_url: str = None,
                 api_key: List[str] = None,
                 max_length: int = None,
                 retry_times: int = 0,
                 is_async: bool = True):
        self.embed_type = embed_type
        self.model = model

        if embed_type == "ollama":
            if base_url is None:
                base_url = "https://localhost:11434"
            if api_key is None:
                api_key = ["ollama"]
        self.base_url = base_url
        self.api_key = api_key or []

        self._api_index = 0

        self.clients: List[OpenAI] = [
            OpenAI(
                api_key=key,
                base_url=self.base_url
            ) for key in self.api_key
        ]
        self.async_clients: List[AsyncOpenAI] = [
            AsyncOpenAI(
                api_key=key,
                base_url=self.base_url
            ) for key in self.api_key
        ]

        if max_length:
            self._MAX_LENGTH = max_length
        else:
            self._MAX_LENGTH = 0

        if retry_times:
            self.retry_times = retry_times
        else:
            self.retry_times = self.retry_times

        self.is_async = is_async

    def _next_client(self,
                     is_async: bool
                     ) -> Union[OpenAI, AsyncOpenAI]:
        if not self.clients:
            self.clients = [OpenAI(base_url=self.base_url)]
            self.async_clients = [AsyncOpenAI(base_url=self.base_url)]
        index = self._api_index % len(self.clients)
        self._api_index += 1

        if is_async:
            return self.async_clients[index]
        else:
            return self.clients[index]

    def embed(self, input_text: List[str]) -> np.ndarray:
        length = len(input_text)
        logging.info(f"This Embedding Process has {length} texts to embed.")
        text_batches: List[List[str]] = self._split_text(input_text)

        if self.is_async:
            try:
                return asyncio.run(self._async_embed(text_batches))
            except RuntimeError as e:
                logging.error(f"Async embedding failed: {e}")
                logging.info("Falling back to synchronous embedding.")
                self.is_async = False
                return self._embed(text_batches)
        else:
            return self._embed(text_batches)

    async def async_embed(self, input_text: List[str]) -> np.ndarray:
        length = len(input_text)
        logging.info(f"This Embedding Process has {length} texts to embed.")
        text_batches: List[List[str]] = self._split_text(input_text)
        embeddings = await self._async_embed(text_batches)
        return embeddings

    def _embed(self, text_batches: List[List[str]]) -> np.ndarray:
        batch_embeddings = []
        for batch in text_batches:
            batch_result = self._bench_embed(batch)
            batch_embeddings.append(batch_result)

        return np.concatenate(batch_embeddings, axis=0)

    async def _async_embed(self, text_batches: List[List[str]]) -> np.ndarray:
        tasks = [self._async_bench_embed(batch) for batch in text_batches]
        batch_embeddings = await asyncio.gather(*tasks)
        return np.concatenate(batch_embeddings, axis=0)

    def _bench_embed(self, batch: List[str]) -> np.ndarray:
        client = self._next_client(is_async=False)
        for attempt in range(self.retry_times):
            try:
                resp = client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                vectors = [record.embedding for record in resp.data]
                embeddings = list2nparray(vectors)
                return embeddings
            except Exception as e:
                logging.warning(
                    f"Sync embed attempt {attempt + 1} failed: {e}")
                if attempt == self.retry_times - 1:
                    raise
                time.sleep(2 ** attempt)

    async def _async_bench_embed(self, batch: List[str]) -> np.ndarray:
        async_client = self._next_client(is_async=True)
        for attempt in range(self.retry_times):
            try:
                resp = await async_client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                vectors = [record.embedding for record in resp.data]
                embeddings = list2nparray(vectors)
                return embeddings
            except Exception as e:
                logging.warning(
                    f"Sync embed attempt {attempt + 1} failed: {e}")
                if attempt == self.retry_times - 1:
                    raise
                time.sleep(2 ** attempt)

    def _split_text(self,
                    input_text: List[str],
                    max_length: int = None) -> List[List[str]]:
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
    from texiv import TexIV
    texiv = TexIV()

    embedder = Embed(
        embed_type="openai",
        model="BAAI/bge-m3",
        base_url="https://api.siliconflow.cn/v1",
        api_key=texiv.API_KEY
    )
    content_1 = "滚滚长江东逝水，浪花淘尽英雄。我曾经仰望天空，想数清楚天空中的云朵到底在想写什么，可是我终究是无法靠近，无法知道它到底在哪里。"
    content_2 = "滚滚长江东逝水，浪花淘尽英雄。我曾经仰望天空，想数清楚天空中的云朵到底在想写什么，可是我终究是无法靠近，无法知道它到底在哪里。"
    content_3 = "滚滚长江东逝水，浪花淘尽英雄。我曾经仰望天空，想数清楚天空中的云朵到底在想写什么，可是我终究是无法靠近，无法知道它到底在哪里。"
    embeddings = asyncio.run(embedder.async_embed(
        [content_1, content_2, content_3]))
    print(embeddings)
    print(type(embeddings))
    print(embeddings.shape)
