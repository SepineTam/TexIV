#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : texiv.py

from typing import Dict, List, Set, Tuple

import numpy as np
import tomllib

from ..config import Config
from .chunk import Chunk
from .embed import Embed
from .filter import Filter
from .similarity import Similarity


class TexIV:
    CONFIG_FILE_PATH = Config().CONFIG_FILE_PATH
    with open(CONFIG_FILE_PATH, "rb") as f:
        cfg = tomllib.load(f)

    # embedding config
    embed_type = cfg.get("embed").get("EMBED_TYPE").lower()
    MAX_LENGTH = cfg.get("embed").get("MAX_LENGTH", 64)
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

    def __init__(self):
        self.chunker = Chunk()
        self.embedder = Embed(embed_type=self.embed_type,
                              model=self.MODEL,
                              base_url=self.BASE_URL,
                              api_key=self.API_KEY,
                              max_length=self.MAX_LENGTH)
        self.similar = Similarity()
        self.filter = Filter(valve=self.valve)

    @staticmethod
    def _description(
            finial_filtered_data: np.ndarray) -> Dict[str, float | int]:
        true_count = int(np.sum(finial_filtered_data))
        total_count = len(finial_filtered_data)
        rate = true_count / total_count
        return {"freq": true_count,
                "count": total_count,
                "rate": rate}

    def embed_keywords(self, keywords: List[str] | Set[str]) -> np.ndarray:
        """Embed keywords using the embedder."""
        if isinstance(keywords, set):
            keywords = list(keywords)
        return self.embedder.embed(keywords)

    def embed_stata_keywords(self, kws: str):
        keywords = set(kws.split())
        return self.embed_keywords(keywords)

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
        embedded_keywords = self.embed_stata_keywords(kws)
        results = [
            self.texiv_one(text, embedded_keywords)
            for text in texts
        ]
        freqs, counts, rates = zip(*results)
        return list(freqs), list(counts), list(rates)
