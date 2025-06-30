# TexIV ado

`texiv` 是一个基于 Python 编写的 Stata 工具包，得益于 Stata 16+ 支持与 Python 联动。

---

A machine learning–based package for transforming text into instrumental variables (IV).

[![PyPI version](https://img.shields.io/pypi/v/texiv.svg)](https://pypi.org/project/texiv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/texiv/issues/new)

## Install (Stata)
If you don't have the package `github`, you can install it with the following command:
```bash
net install github , from ("https://raw.githubusercontent.com/haghish/github/master/")
```

Then, you can install `texiv` with command `github`:
```bash
github install SepineTam/TexIV
```

If there is still any problem, you can use `db github` to the GUI installation.
Enter:
```toml
keywords = "texiv"
language = "Python"
```

Then you can see the return
```stata
. github search texiv, language(Python) in("name")

 ----------------------------------------------------------------------------------
  Repository      Username    Install  Description 
 ----------------------------------------------------------------------------------
  TexIV           SepineTam   Install  A machine learning–based package for
                              1167k    transforming text into instrumental
                                       variables (IV).
                                       updated on 2025-06-30
                                       Fork:0    Star:1    Lang:Python      

 ----------------------------------------------------------------------------------
```

Click Install, and then you can install the package to Stata.

## Install (Python)
The necessary one is the Python part, and also the most difficult one. 

To be honest, the installation of `texiv` is not very convenient, but it is not too difficult either. You need to find the python which is integrated with Stata, and then install the package using pip. For more details, please refer to the following:

- For Windows: [Stata Offical Guide](https://www.stata.com/features/overview/pystata-python-integration), [连享会](https://www.lianxh.cn/details/553.html)

- For macOS: follow my words ~

First of all, you need to find which Python it is with the command `python query`, then there will be a list of the Python, may be the first is the one you want, but it is not always the case, so you need to check the version of Python, and find the one which is integrated with Stata. For example, if you see something like this:

```
. python query
------------------------------------------------------------------------------------------------------------------------
    Python Settings
      set python_exec      /usr/local/bin/python3
      set python_userpath  

    Python system information
      initialized          yes
      version              3.13.2
      architecture         64-bit
      library path         /Library/Frameworks/Python.framework/Versions/3.13/lib/libpython3.13.dylib
```
Then please go to your terminal
```bash
sudo -H /usr/local/bin/python3 -m pip install --upgrade texiv
```
If you are located in China, change the follow command:
```bash
sudo -H /usr/local/bin/python3 -m pip install --upgrade texiv -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
```

## Usage
For the first use, you should config your embedding model and type, more information please refer to [Proj README](../../README.md)

In Stata, you can use the command `texiv` to make your String variable into number type more over make it be your IV.

```Stata
texiv varname, kws(string)
```

Example:
Image we have a variable named `reports`, and we hope to calculate the reports' 数字化水平 about the local government.
```Stata
texiv reports, kws("数字化 智能化 人工智能 科技创新 云计算 物联网 ...")
```
Then we will have 3 new cols data in your Stata data set.

