#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : texiv.py

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
    embed_type = cfg.get("embed").get("EMBED_TYPE").lower()
    MAX_LENGTH = cfg.get("embed").get("MAX_LENGTH", 64)
    IS_ASYNC = cfg.get("embed").get("IS_ASYNC", False)
    MODEL = cfg.get("embed").get(embed_type).get("MODEL")
    BASE_URL = cfg.get("embed").get(embed_type).get("BASE_URL")
    API_KEY = cfg.get("embed").get(embed_type).get("API_KEY")

    # texiv config
    texiv_cfg = cfg.get("texiv")
    stopwords_path = texiv_cfg.get("chunk").get("stopwords_path")
    if stopwords_path == "":
        stopwords_path = None
    SIMILARITY_MTHD = texiv_cfg.get("similarity").get("MTHD")
    VALVE_TYPE = texiv_cfg.get("filter").get("VALVE_TYPE")
    valve = texiv_cfg.get("filter").get("valve")

    def __init__(self, valve: float = 0.0):
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
        self.filter = Filter(valve=self.valve)

    @staticmethod
    def _description(
            finial_filtered_data: np.ndarray
    ) -> Dict[str, float | int]:
        true_count = int(np.sum(finial_filtered_data))
        total_count = len(finial_filtered_data)
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

    def texiv_one(self,
                  content: str,
                  embedded_keywords: np.ndarray) -> Tuple[int, int, float]:
        """Process a single content with keywords."""
        chunked_content = self.chunker.segment_from_text(content)
        embedded_chunked_content = self.embedder.embed(chunked_content)
        dist_array = self.similar.similarity(embedded_chunked_content,
                                             embedded_keywords)

        filtered = self.filter.filter(dist_array)
        two_stage_filtered = self.filter.two_stage_filter(filtered)

        true_count = int(np.sum(two_stage_filtered))
        total_count = len(two_stage_filtered)
        return true_count, total_count, true_count / total_count

    def texiv_stata(self, texts: List[str], kws: str):
        embedded_keywords = self._embed_keywords(kws)
        results = [
            self.texiv_one(text, embedded_keywords)
            for text in texts
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
        results = [
            self.texiv_one(text, embedded_keywords)
            for text in extract_col
        ]
        freqs, counts, rates = zip(*results)
        df[col_name+"freq"] = freqs
        df[col_name+"count"] = counts
        df[col_name+"rate"] = rates
        return df
