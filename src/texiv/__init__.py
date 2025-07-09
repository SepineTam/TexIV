#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

from importlib.metadata import version

from .core import TexIV
from .stata import StataTexIV

__version__ = version("texiv")

__all__ = [
    "TexIV",
    "StataTexIV"
]
