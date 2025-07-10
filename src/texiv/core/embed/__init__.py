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
from collections import deque
from typing import Deque, List, Set, Union

import numpy as np
from openai import AsyncOpenAI, OpenAI

from ..utils import list2nparray


class Embed:
    _MAX_LENGTH = 64
    retry_times = 3

    def __init__(self,
                 embed_type: str = None,
                 model: str = None,
                 base_url: str = None,
                 api_key: List[str] = None,
                 max_length: int = None,
                 retry_times: int = None,
                 is_async: bool = True,
                 max_concurrency: int | None = None):
        self.embed_type = embed_type
        self.model = model

        if embed_type == "ollama":
            if base_url is None:
                base_url = "https://localhost:11434"
            if api_key is None:
                api_key = ["ollama"]
        self.base_url = base_url
        self.api_key = api_key or []

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

        # initialize pools
        self._idle_clients: Deque[OpenAI] = deque(self.clients)
        self._using_clients: Set[OpenAI] = set()
        self._async_idle_clients: Deque[AsyncOpenAI] = deque(
            self.async_clients)
        self._async_using_clients: Set[AsyncOpenAI] = set()

        self._pool_lock = asyncio.Lock()

        if max_concurrency is None:
            max_concurrency = len(self.async_clients)
        self._max_concurrency = max(
            1, min(len(self.async_clients), max_concurrency))
        self._semaphore = asyncio.Semaphore(self._max_concurrency)

        if max_length:
            self._MAX_LENGTH = max_length
        else:
            self._MAX_LENGTH = 0

        if retry_times:
            self.retry_times = retry_times
        else:
            self.retry_times = self.retry_times

        self.is_async = is_async

    def _acquire_client(self, is_async: bool) -> Union[OpenAI, AsyncOpenAI]:
        """Get a client from idle pool and put it in using pool."""
        if is_async:
            client = self._async_idle_clients.popleft()
            self._async_using_clients.add(client)
        else:
            client = self._idle_clients.popleft()
            self._using_clients.add(client)
        return client

    def _release_client(self,
                        client: Union[OpenAI,
                                      AsyncOpenAI],
                        is_async: bool) -> None:
        """Return client to idle pool from using pool."""
        if is_async:
            self._async_using_clients.discard(client)
            self._async_idle_clients.append(client)
        else:
            self._using_clients.discard(client)
            self._idle_clients.append(client)

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
        client = self._acquire_client(is_async=False)
        try:
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
        finally:
            self._release_client(client, is_async=False)

    async def _async_bench_embed(self, batch: List[str]) -> np.ndarray:
        async with self._semaphore:
            async with self._pool_lock:
                async_client = self._acquire_client(is_async=True)
            try:
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
            finally:
                async with self._pool_lock:
                    self._release_client(async_client, is_async=True)

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
