#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : utils.py

from typing import List

import numpy as np


def list2nparray(data: List[List[float]]) -> np.ndarray:
    return np.array(data, dtype=np.float64)
