<p align="center">
  <img src="source/img/TexIV-logo_16_9.png" width="256" alt="TexIV Logo">
</p>

---
A machine learning–based package for transforming text into instrumental variables (IV).

![PythonMin](https://img.shields.io/badge/Python-3.11+-yellow) 
![StataMin](https://img.shields.io/badge/Stata-17+-blue) 
[![PyPI version](https://img.shields.io/pypi/v/texiv.svg)](https://pypi.org/project/texiv/)
[![PyPI Downloads](https://static.pepy.tech/badge/texiv)](https://pepy.tech/projects/texiv)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/texiv/issues/new)
![release](https://img.shields.io/github/release-date/sepinetam/texiv)
[![Wiki](https://img.shields.io/badge/Doc-Wiki-blue.svg)](https://github.com/sepinetam/texiv/wiki)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/SepineTam/TexIV)

---

## 🌰 Example
Visit [Stata Example File](source/example/dofiles/main.do) and [Python Example File](source/example/pyscript/main.py).

There is a step-by-step example.

## ✨ Feature

- Support multiple Chinese word segmentation and embedding methods
- Customizable stopwords
- Support keyword relevance filtering and two-stage filtering
- Output includes frequency, total count, and ratio statistics

## 📦 Requirements

- Python 3.11+
- Recommended to use virtual environment (e.g., `venv` or `conda`)

## 🚀 Quickly Start

### Install
```bash
pip install texiv
```

### Usage
```python
from typing import List

from texiv import TexIV

texiv = TexIV()
content: str = "This is a test text..."
keywords: List[str] = ["keyword1", "keyword2", "keyword3"]
texiv.texiv_it(content, keywords)
```

Async usage:

```python
import asyncio
from typing import List

from texiv import AsyncTexIV, set_parallel_count

# Set the default concurrency for new AsyncTexIV instances.
set_parallel_count(10)

texiv = AsyncTexIV()
content: str = "This is a test text..."
keywords: List[str] = ["keyword1", "keyword2", "keyword3"]
result = asyncio.run(texiv.texiv_it(content, keywords))
```

For DataFrame processing, call the async API from an event loop:

```python
import asyncio
import pandas as pd

from texiv import AsyncTexIV, set_parallel_count

async def main():
    set_parallel_count(10)
    texiv = AsyncTexIV()
    df = pd.DataFrame({"text": ["First document", "Second document"]})
    return await texiv.texiv_df(df, "text", ["document"])

result_df = asyncio.run(main())
```

`set_parallel_count()` only affects `TexIV` or `AsyncTexIV` instances created after it is called. You can also pass `max_concurrency=` directly to an instance when you need per-instance control.

Output example:

```
{'freq': 7, 'count': 34, 'rate': 0.20588235294117646}
```

## 🖥️ Command Line Tool

The project also provides a command-line interface that can be used directly after installation:

```bash
texiv --help
```

## 🛠️ Configuration

All models and parameters can be adjusted through configuration files in `～/.texiv/config.toml`.


## 📄 License
This project is licensed under the GNU Affero General Public License v3.0. See [LICENSE](LICENSE) for details.

**Note:** Commercial use requires compliance with AGPL-3.0 terms, including source code disclosure for network services.
