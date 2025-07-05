* If you don't have github command, install it first
* net install github, from("https://haghish.github.io/github/")

* Install the package from GitHub
github install SepineTam/TexIV, replace

* Make sure you have a Stata*Python environment set up
* Find your python in Stata, and install the necessary with command below
* python -m pip install --upgrade texiv
* Warning: maybe there is a little mistake while installing python dependencies.
* More information you can visit the website https://www.lianxh.cn/details/553.html

* Please make sure you should make your config to your computer for avoiding config it each time.
* In terminal use `texiv --init`

* Now, I think you have ever do everything what we should do.
* Let's start!

* Load data from GitHub
use "https://raw.githubusercontent.com/SepineTam/TexIV/master/source/example/data/shanghai_reports.dta", clear

* Or you can use the data from your local disk
* use source/example/data/shanghai_reports.dta, clear
texiv report, kws("政府 数字化 经济发展 互联网 物联网 新质生产力 中国制造 产业升级")

