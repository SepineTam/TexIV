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

_pending_valve_registrations: Dict[str, Callable] = {}
_pending_two_stage_registrations: Dict[str, Callable] = {}


def _valve_register(valve_type: str):
    def decorator(func: Callable):
        _pending_valve_registrations[valve_type] = func
        return func
    return decorator


def _two_stage_register(CALCU_MTHD: str):
    def decorator(func: Callable):
        _pending_two_stage_registrations[CALCU_MTHD] = func
        return func
    return decorator


class Filter:
    VALVE_TYPE: str = "value"
    CALCU_MTHD: str = "any"
    valve: float = 0.6
    _valves: Dict[str, Callable] = {}
    _two_stages: Dict[str, Callable] = {}

    def __init__(self,
                 valve: float | None = None,
                 VALVE_TYPE: str | None = None,
                 CALCU_MTHD: str | None = None):
        if valve:
            self.valve = valve
        if VALVE_TYPE:
            self.VALVE_TYPE = VALVE_TYPE
        if CALCU_MTHD:
            self.CALCU_MTHD = CALCU_MTHD

        self._valves.update(_pending_valve_registrations)
        self._two_stages.update(_pending_two_stage_registrations)

    def filter(self, dist: np.ndarray, **kwargs) -> np.ndarray:
        fn = self._valves[self.VALVE_TYPE]
        return fn(self, dist, **kwargs)

    def two_stage_filter(self, matrix: np.ndarray) -> np.ndarray:
        fn = self._two_stages[self.CALCU_MTHD]
        return fn(matrix)

    @_valve_register("value")
    def _filter_with_value(self,
                           dist: np.ndarray,
                           valve: float = 0.0) -> np.ndarray:
        if valve:  # if 0.0 -> False
            return dist >= valve
        else:
            return dist >= self.valve

    @_valve_register("array")
    def _filter_with_array(self,
                           dist: np.ndarray,
                           valve_array: np.ndarray) -> np.ndarray:
        return dist >= valve_array

    @staticmethod
    @_two_stage_register("any")
    def row_any_true(matrix: np.ndarray) -> np.ndarray:
        return np.any(matrix, axis=1)

    @staticmethod
    @_two_stage_register("all")
    def row_all_true(matrix: np.ndarray) -> np.ndarray:
        return np.all(matrix, axis=1)

    @staticmethod
    @_two_stage_register("majority")
    def row_majority_true(matrix: np.ndarray) -> np.ndarray:
        true_counts = np.sum(matrix, axis=1)
        m = matrix.shape[1]
        return true_counts >= (m - true_counts)
