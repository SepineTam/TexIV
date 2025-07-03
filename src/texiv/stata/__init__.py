from typing import List

from ..core import TexIV


class StataTexIV:
    @staticmethod
    def texiv(Data, varname: str, kws: str):
        texiv = TexIV()
        contents: List[str] = Data.get(varname)
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
