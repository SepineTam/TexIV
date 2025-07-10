#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

from typing import Dict, List

from ..core import TexIV


class StataTexIV:
    @staticmethod
    def is_exist_var(Data,
                     *var_names) -> Dict[str, bool]:
        result: Dict[str, bool] = {}
        for var_name in var_names:
            try:
                Data.getVarIndex(var_name)
                result[var_name] = True
            except ValueError:
                result[var_name] = False
        return result

    @staticmethod
    def check_is_async(is_async) -> bool:
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
        return is_async

    @staticmethod
    def texiv(Data,
              varname: str,
              kws: str,
              is_async: bool = True):
        is_async = StataTexIV.check_is_async(is_async)
        texiv = TexIV(is_async=is_async)

        try:
            contents: List[str] = Data.get(varname)
        except ValueError as e:
            raise NameError("Don't find the variable, please check the varname.") from e

        # define the var name
        true_count_varname = f"{varname}_freq"
        total_count_varname = f"{varname}_count"
        rate_varname = f"{varname}_rate"

        var_exist_state = StataTexIV.is_exist_var(Data,
                                                  true_count_varname,
                                                  total_count_varname,
                                                  rate_varname)
        if any(var_exist_state.values()):
            existing_vars = [var for var, exists in var_exist_state.items() if exists]
            raise ValueError(f"Existing {existing_vars}, please drop them and retry.")

        Data.addVarInt(true_count_varname)
        Data.addVarInt(total_count_varname)
        Data.addVarFloat(rate_varname)

        # back to do not support async in the sense of df-face
        freqs, counts, rates = texiv.texiv_stata(contents, kws)

        Data.store(true_count_varname, None, freqs)
        Data.store(total_count_varname, None, counts)
        Data.store(rate_varname, None, rates)
