#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

from typing import List

from ..core import TexIV


class StataTexIV:
    @staticmethod
    def texiv(Data,
              varname: str,
              kws: str,
              is_async: bool = True):
        if not isinstance(is_async, bool):
            if isinstance(is_async, int) or isinstance(is_async, float):
                is_async = bool(is_async)
            elif isinstance(is_async, str):
                true_list = ["true", "yes", "1", "on"]
                is_async = is_async.lower() in true_list
            else:
                if is_async is not None:
                    is_async = True
        else:
            is_async = is_async
        texiv = TexIV(is_async=is_async)
        contents: List[str] = Data.get(varname)

        # back to do not support async in the sense of df-face
        freqs, counts, rates = texiv.texiv_stata(contents, kws)

        true_count_varname = f"{varname}_freq"
        total_count_varname = f"{varname}_count"
        rate_varname = f"{varname}_rate"

        Data.addVarInt(true_count_varname)
        Data.addVarInt(total_count_varname)
        Data.addVarFloat(rate_varname)

        Data.store(true_count_varname, None, freqs)
        Data.store(total_count_varname, None, counts)
        Data.store(rate_varname, None, rates)
