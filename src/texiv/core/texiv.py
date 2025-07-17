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
from ..utils import create_rich_helper
from .chunk import Chunk
from .embed import Embed
from .filter import Filter
from .similarity import Similarity


class TexIV:
    CONFIG_FILE_PATH = Config.CONFIG_FILE_PATH

    def __init__(
            self,
            valve: float = 0.0,
            is_async: bool = True,
            rich_helper=None):
        """
        Initialize TexIV with configuration.

        Args:
            valve: The threshold value for filtering (0.0-1.0)
            is_async: Whether to use async operations
            rich_helper: RichHelper instance for rich output
        """
        self.rich_helper = rich_helper or create_rich_helper()

        if not Config.is_exist():
            # In test environment, skip interactive prompt
            if 'pytest' not in sys.modules:
                from .utils import yes_or_no
                self.rich_helper.print_error(
                    "Configuration file not found. "
                    "Please ensure the file exist!\n"
                    "You can use `texiv --init` in terminal to create a default config.")
                __is_init = yes_or_no(
                    "Do you want to create a default config file?")
                if not __is_init:
                    sys.exit(1)
                else:
                    Config()
            else:
                raise FileNotFoundError("Configuration file not found")

        with open(self.CONFIG_FILE_PATH, "rb") as f:
            self.cfg = tomllib.load(f)

        # embedding config
        self.embed_type: str = self.cfg.get("embed").get("EMBED_TYPE").lower()
        self.MAX_LENGTH: int = self.cfg.get("embed").get("MAX_LENGTH", 64)
        self.IS_ASYNC: bool = self.cfg.get("embed").get("IS_ASYNC", False)
        self.MODEL: str = self.cfg.get("embed").get(
            self.embed_type).get("MODEL")
        self.BASE_URL: str = self.cfg.get("embed").get(
            self.embed_type).get("BASE_URL")
        self.API_KEY: List[str] = self.cfg.get(
            "embed").get(self.embed_type).get("API_KEY")

        # texiv config
        texiv_cfg = self.cfg.get("texiv")
        stopwords_path = texiv_cfg.get("chunk").get("stopwords_path")
        if stopwords_path == "":
            stopwords_path = None
        self.SIMILARITY_MTHD = texiv_cfg.get("similarity").get("MTHD")
        self.VALVE_TYPE = texiv_cfg.get("filter").get("VALVE_TYPE")
        self.valve = texiv_cfg.get("filter").get("valve")

        # Override async setting if specified
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
            stopwords: List[str] | None = None) -> Dict[str, float | int]:
        """Process text content with keywords to find instrumental variables.

        Args:
            content: The text content to analyze
            keywords: List of keywords to search for
            stopwords: Optional list of stopwords to filter out

        Returns:
            Dictionary containing processing results with freq, count, and rate
        """
        if stopwords:
            self.chunker.load_stopwords(stopwords)

        with self.rich_helper.create_progress("Processing text analysis") as progress:
            task = progress.add_task("Processing", total=5)

            # Step 1: Chunk content
            chunked_content = self.chunker.segment_from_text(content)
            progress.update(task, advance=1, description="Chunking content")

            # Step 2: Embed chunked content
            embedded_chunked_content = self.embedder.embed(chunked_content)
            progress.update(
                task,
                advance=1,
                description="Embedding content chunks")

            # Step 3: Embed keywords
            embedded_keywords = self.embedder.embed(keywords)
            progress.update(task, advance=1, description="Embedding keywords")

            # Step 4: Calculate similarity
            dist_array = self.similar.similarity(embedded_chunked_content,
                                                 embedded_keywords)
            progress.update(
                task,
                advance=1,
                description="Calculating similarity")

            # Step 5: Filter results
            filtered = self.filter.filter(dist_array)
            two_stage_filtered = self.filter.two_stage_filter(filtered)
            progress.update(task, advance=1, description="Filtering results")

        results = self._description(two_stage_filtered)

        # Display results
        self.rich_helper.display_status_panel(
            "Analysis Results",
            {
                "Keywords Found": str(results["freq"]),
                "Total Chunks": str(results["count"]),
                "Match Rate": f"{results['rate']:.2%}",
                "Keywords": ", ".join(keywords[:5]) + ("..." if len(keywords) > 5 else "")
            }
        )

        return results

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

    def texiv_stata(self,
                    texts: List[str],
                    kws: str) -> Tuple[List[int],
                                       List[int],
                                       List[float]]:
        """Process multiple texts with keywords for Stata integration.

        Args:
            texts: List of text strings to analyze
            kws: Keywords string to search for

        Returns:
            Tuple of (frequencies, counts, rates) lists
        """
        total_texts = len(texts)

        with self.rich_helper.create_progress(f"Processing {total_texts} texts") as progress:
            task = progress.add_task("Processing texts", total=total_texts)

            embedded_texts = self._embed_content(texts)
            embedded_keywords = self._embed_keywords(kws)

            results = []
            for i, embedded_text in enumerate(embedded_texts):
                result = self._texiv_embedded(embedded_text, embedded_keywords)
                results.append(result)
                progress.update(
                    task,
                    advance=1,
                    description=f"Processing text {i+1}/{total_texts}")

            freqs, counts, rates = zip(*results)

            # Display summary
            summary = {
                "Total Texts": str(total_texts),
                "Avg Keywords Found": f"{sum(freqs)/len(freqs):.2f}",
                "Avg Match Rate": f"{sum(rates)/len(rates):.2%}",
                "Keywords": kws
            }
            self.rich_helper.display_results_table(
                "Stata Processing Summary", summary)

            return list(freqs), list(counts), list(rates)

    def texiv_df(self,
                 df: pd.DataFrame,
                 col_name: str,
                 kws: List[str] | Set[str] | str) -> pd.DataFrame:
        """Process a DataFrame with a specified column and keywords.

        Args:
            df: pandas DataFrame containing the data
            col_name: name of the column to analyze
            kws: keywords to search for (string, list, or set)

        Returns:
            DataFrame with additional columns for analysis results
        """
        total_rows = len(df)
        embedded_keywords = self._embed_keywords(kws)
        extract_col = df[col_name].astype(str).tolist()

        with self.rich_helper.create_progress(f"Processing DataFrame ({total_rows} rows)") as progress:
            task = progress.add_task("Processing rows", total=total_rows)

            embedded_texts = self._embed_content(extract_col)
            results = []
            for i, embedded_text in enumerate(embedded_texts):
                result = self._texiv_embedded(embedded_text, embedded_keywords)
                results.append(result)
                progress.update(
                    task,
                    advance=1,
                    description=f"Processing row {i+1}/{total_rows}")

        df = _write_result_to_df(df, col_name, results)

        # Display summary
        freqs = df[col_name + "_freq"].tolist()
        rates = df[col_name + "_rate"].tolist()

        summary = {
            "Total Rows": str(total_rows),
            "Processed Column": col_name,
            "Keywords": str(kws) if len(
                str(kws)) <= 50 else str(kws)[
                :47] + "...",
            "Avg Keywords Found": f"{sum(freqs)/len(freqs):.2f}",
            "Avg Match Rate": f"{sum(rates)/len(rates):.2%}",
            "Max Keywords Found": str(
                max(freqs)),
            "Min Keywords Found": str(
                min(freqs))}
        self.rich_helper.display_results_table(
            "DataFrame Processing Summary", summary)

        return df

    def texiv_api(self,
                  df: pd.DataFrame,
                  col_name: str,
                  kws: List[str]) -> pd.DataFrame:
        """API-style processing of DataFrame with keywords.

        Args:
            df: pandas DataFrame containing the data
            col_name: name of the column to analyze
            kws: list of keywords to search for

        Returns:
            DataFrame with additional columns for analysis results
        """
        return self.texiv_df(df, col_name, kws)


def _write_result_to_df(
        df: pd.DataFrame,
        col_name: str,
        results: Tuple) -> pd.DataFrame:
    freqs, counts, rates = zip(*results)
    df[col_name + "_freq"] = freqs
    df[col_name + "_count"] = counts
    df[col_name + "_rate"] = rates
    return df
