#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : texiv.py

import asyncio
import sys
from typing import Dict, List, Set, Tuple

import numpy as np
import pandas as pd
import tomllib

from ..config import Config
from .chunk import Chunk
from .embed import Embed
from .filter import Filter
from .similarity import Similarity
from .utils import yes_or_no


class TexIV:
    CONFIG_FILE_PATH = Config.CONFIG_FILE_PATH
    if not Config.is_exist():
        print(
            "Configuration file not found. "
            "Please ensure the file exist!\n"
            "You can use `texiv --init` in terminal to create a default config.")
        __is_init = yes_or_no("Do you want to create a default config file?")
        if not __is_init:
            sys.exit(1)
        else:
            Config()
    with open(CONFIG_FILE_PATH, "rb") as f:
        cfg = tomllib.load(f)

    # embedding config
    embed_type: str = cfg.get("embed").get("EMBED_TYPE").lower()
    MAX_LENGTH: int = cfg.get("embed").get("MAX_LENGTH", 64)
    IS_ASYNC: bool = cfg.get("embed").get("IS_ASYNC", False)
    MODEL: str = cfg.get("embed").get(embed_type).get("MODEL")
    BASE_URL: str = cfg.get("embed").get(embed_type).get("BASE_URL")
    API_KEY: List[str] = cfg.get("embed").get(embed_type).get("API_KEY")

    # texiv config
    texiv_cfg = cfg.get("texiv")
    stopwords_path = texiv_cfg.get("chunk").get("stopwords_path")
    if stopwords_path == "":
        stopwords_path = None
    SIMILARITY_MTHD = texiv_cfg.get("similarity").get("MTHD")
    VALVE_TYPE = texiv_cfg.get("filter").get("VALVE_TYPE")
    valve = texiv_cfg.get("filter").get("valve")

    def __init__(self, valve: float = 0.0, is_async: bool = True):
        self.IS_ASYNC: bool = is_async & self.IS_ASYNC
        self.chunker = Chunk()
        self.embedder = Embed(embed_type=self.embed_type,
                              model=self.MODEL,
                              base_url=self.BASE_URL,
                              api_key=self.API_KEY,
                              max_length=self.MAX_LENGTH,
                              is_async=self.IS_ASYNC)
        self.similar = Similarity()

        if 0.0 < valve < 1.0:
            self.valve = valve
        else:
            self.valve = self.valve
        self.filter = Filter(valve=self.valve)

    @staticmethod
    def _description(
            final_filtered_data: np.ndarray
    ) -> Dict[str, float | int]:
        true_count = int(np.sum(final_filtered_data))
        total_count = len(final_filtered_data)
        rate = true_count / total_count
        return {"freq": true_count,
                "count": total_count,
                "rate": rate}

    def _embed_keywords(self, kws: str | List[str] | Set[str]) -> np.ndarray:
        if isinstance(kws, str):
            keywords = set(kws.split())
        elif isinstance(kws, set):
            keywords = list(kws)
        elif isinstance(kws, list):
            keywords = list(set(kws))
        else:
            raise TypeError("Keywords must be a string, list, or set.")

        return self.embedder.embed(keywords)

    def _embed_chunked_content(self, content: List[str]) -> np.ndarray:
        """Embed chunked content."""
        return self.embedder.embed(content)

    async def _async_embed_chunked_content(self, content: List[str]) -> np.ndarray:
        """Async embed chunked content."""
        return await self.embedder.async_embed(content)

    def _embed_content(self,
                       content: str | List[str]) -> List[np.ndarray]:
        if isinstance(content, str):
            # if the upload content is one string
            chunked_content: List[str] = self.chunker.segment_from_text(
                content)
            return [self._embed_chunked_content(chunked_content)]
        elif isinstance(content, list):
            # if there are lots of string which conducted into a list
            embedded_content_list: List[np.ndarray] = []
            for item in content:
                chunked_item = self.chunker.segment_from_text(item)
                embedded_content_list.append(
                    self._embed_chunked_content(chunked_item))
            return embedded_content_list
        else:
            raise TypeError("Content must be a string or list.")

    async def _async_embed_content(self,
                                   content: str | List[str]) -> List[np.ndarray]:
        if isinstance(content, str):
            chunked_content = self.chunker.segment_from_text(content)
            return [await self._async_embed_chunked_content(chunked_content)]
        elif isinstance(content, list):
            tasks = [
                self._async_embed_chunked_content(
                    self.chunker.segment_from_text(item)
                )
                for item in content
            ]
            results_tuple = await asyncio.gather(*tasks)
            return list(results_tuple)
        else:
            raise TypeError("Content must be a string or list.")

    def texiv_it(
            self,
            content: str,
            keywords: List[str],
            stopwords: List[str] | None = None):
        if stopwords:
            self.chunker.load_stopwords(stopwords)
        chunked_content = self.chunker.segment_from_text(content)
        embedded_chunked_content = self.embedder.embed(chunked_content)
        embedded_keywords = self.embedder.embed(keywords)
        dist_array = self.similar.similarity(embedded_chunked_content,
                                             embedded_keywords)

        filtered = self.filter.filter(dist_array)
        two_stage_filtered = self.filter.two_stage_filter(filtered)
        return self._description(two_stage_filtered)

    def _texiv_embedded(self,
                        embedded_chunked_content: np.ndarray,
                        embedded_keywords: np.ndarray) -> Tuple[int,
                                                                int,
                                                                float]:
        """
        Process a single content with keywords.
        """
        dist_array = self.similar.similarity(embedded_chunked_content,
                                             embedded_keywords)

        filtered = self.filter.filter(dist_array)
        two_stage_filtered = self.filter.two_stage_filter(filtered)

        true_count = int(np.sum(two_stage_filtered))
        total_count = len(two_stage_filtered)
        return true_count, total_count, true_count / total_count

    def texiv_stata(self, texts: List[str], kws: str):
        embedded_texts = self._embed_content(texts)
        embedded_keywords = self._embed_keywords(kws)
        results = [
            self._texiv_embedded(embedded_text, embedded_keywords)
            for embedded_text in embedded_texts
        ]
        freqs, counts, rates = zip(*results)
        return list(freqs), list(counts), list(rates)

    def texiv_df(self,
                 df: pd.DataFrame,
                 col_name: str,
                 kws: List[str] | Set[str] | str) -> pd.DataFrame:
        """Process a DataFrame with a specified column and keywords."""
        embedded_keywords = self._embed_keywords(kws)
        extract_col = df[col_name].astype(str).tolist()

        embedded_texts = self._embed_content(extract_col)
        results = [
            self._texiv_embedded(embedded_text, embedded_keywords)
            for embedded_text in embedded_texts
        ]
        freqs, counts, rates = zip(*results)
        df[col_name + "_freq"] = freqs
        df[col_name + "_count"] = counts
        df[col_name + "_rate"] = rates
        return df
