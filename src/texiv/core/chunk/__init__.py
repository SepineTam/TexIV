#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

import logging
import os
from typing import List, Set

import jieba


def merge_multi_stopwords(file_paths: List[str]) -> Set[str]:
    all_stopwords = set()

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                stopwords = f.read().split()
                all_stopwords.update(stopwords)
        except FileNotFoundError:
            logging.error(
                f"Warning: Could not find the file {file_path}, continue")
        except Exception as e:
            logging.error(f"When reading file {file_path} Error: {e}")

    return all_stopwords


def get_txt_file_paths(subdir: str) -> List[str]:
    pwd = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(pwd, subdir)
    txt_paths = []
    for root, _, files in os.walk(target_dir):
        for filename in files:
            if filename.lower().endswith('.txt'):
                txt_paths.append(os.path.join(root, filename))
    return txt_paths


file_list: List[str] = get_txt_file_paths("stopwords")
_default_stopwords: Set[str] = merge_multi_stopwords(file_list)


class Chunk:
    stopwords: Set[str] = _default_stopwords

    def __init__(self, stopwords: Set[str] | List[str] = None):
        self.load_stopwords(stopwords)

    def load_stopwords(self, stopwords: Set[str] | List[str] = None):
        if stopwords:
            self.stopwords = set(stopwords)

    def load_stopwords_file(self, stopwords_file_path: str):
        with open(stopwords_file_path, "r") as f:
            stopwords = f.read().split()
        self.load_stopwords(stopwords)

    def _base_segment(self, text: str) -> List[str]:
        words = jieba.lcut(text)
        filtered = [w for w in words if w.strip() and w not in self.stopwords]
        return filtered

    def segment_from_file(self, file_path: str) -> List[str]:
        with open(file_path, "r") as f:
            content = f.read()
        return self._base_segment(content)

    def segment_from_text(self, text: str) -> List[str]:
        return self._base_segment(text)


if __name__ == "__main__":
    chunker = Chunk()
