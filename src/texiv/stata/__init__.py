from ..core import TexIV


class StataTexIV:
    @staticmethod
    def texiv(Data, varname, kws):
        texiv = TexIV()
        contents = Data.get(varname)
        freqs, counts, rates = texiv.texiv_stata(contents, kws)

        true_count_varname = f"{varname}_freq"
        total_count_varname = f"{varname}_count"
        rate_varname = f"{varname}_rate"

        Data.store(true_count_varname, None, freqs)
        Data.store(total_count_varname, None, counts)
        Data.store(rate_varname, None, rates)
