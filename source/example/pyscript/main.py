import pandas as pd
from pandas import pandas
from texiv import TexIV

data_path = "../data/shanghai_reports.dta"
df: pd.DataFrame = pd.read_stata(data_path)

texiv = TexIV()
kws = "政府 数字化 经济发展 互联网 物联网 新质生产力 中国制造 产业升级"

texts = df["report"].to_list()
des_freq, des_count, des_rate = texiv.texiv_stata(texts, kws)

df["texiv_freq"] = des_freq
df["texiv_count"] = des_count
df["texiv_rate"] = des_rate

df.to_csv("../data/shanghai_reports_texiv.csv", index=False)
