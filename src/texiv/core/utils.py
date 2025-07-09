#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : utils.py

from typing import List

import numpy as np


def list2nparray(data: List[List[float]]) -> np.ndarray:
    return np.array(data, dtype=np.float64)


def yes_or_no(msg: str) -> bool:
    """Prompt user for yes or no input."""
    while True:
        response = input(msg + "(Y/n): ").strip().lower()
        if response in ('yes', 'y'):
            return True
        elif response in ('no', 'n'):
            return False
        else:
            print("Please answer with '[Y]es' or 'no'.")
