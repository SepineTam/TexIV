#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

from typing import Callable, Dict

import numpy as np

from ..utils import list2nparray

_pending_calculation_registrations: Dict[str, Callable] = {}


def _register(MTHD: str):
    def decorator(func: Callable):
        _pending_calculation_registrations[MTHD] = func
        return func
    return decorator


class Similarity:
    MTHD = "cosine"
    _similarities: Dict[str, Callable] = {}

    def __init__(self, MTHD: str = None):
        if MTHD:
            self.MTHD = MTHD
        self._similarities.update(_pending_calculation_registrations)

    def similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        fn = self._similarities[self.MTHD]
        return fn(a, b)

    @staticmethod
    @_register(MTHD="cosine")
    def _cosine_similarity_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if isinstance(a, list):
            a = list2nparray(a)
        if isinstance(b, list):
            b = list2nparray(b)
        a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
        b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
        return np.dot(a_norm, b_norm.T)
