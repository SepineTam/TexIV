# TexIV User Guide / TexIV用户指南

<p align="center">
  <img src="../img/TexIV-logo_16_9.png" width="256" alt="TexIV Logo">
</p>

---

## 📖 Quick Start / 快速开始

### Installation / 安装

```bash
pip install texiv
```

### Basic Usage / 基本用法

**English:**
```python
from texiv import TexIV

# Initialize TexIV
texiv = TexIV()

# Your text content
text = "Digital transformation is reshaping the economy through intelligent technologies."
keywords = ["digital", "transformation", "technology"]

# Get IV statistics
result = texiv.texiv_it(text, keywords)
print(result)
# Output: {'freq': 5, 'count': 12, 'rate': 0.4167}
```

**中文:**
```python
from texiv import TexIV

# 初始化TexIV
texiv = TexIV()

# 文本内容
text = "数字化转型正在通过智能技术重塑经济结构。"
keywords = ["数字化", "转型", "技术"]

# 获取IV统计
result = texiv.texiv_it(text, keywords)
print(result)
# 输出: {'freq': 5, 'count': 12, 'rate': 0.4167}
```

---

## 🔧 Configuration / 配置

### Configuration File / 配置文件

**English:** TexIV uses `~/.texiv/config.toml` for configuration. Create it if it doesn't exist:

**中文:** TexIV使用`~/.texiv/config.toml`进行配置。如果文件不存在，请创建：

```toml
[embed]
EMBED_TYPE = "openai"  # "openai" or "ollama"
MAX_LENGTH = 64
IS_ASYNC = false

[embed.openai]
MODEL = "BAAI/bge-m3"
BASE_URL = "https://api.openai.com/v1"
API_KEY = ["your-api-key-1", "your-api-key-2"]

[embed.ollama]
MODEL = "bge-m3:latest"
BASE_URL = "http://localhost:11434"
API_KEY = ["ollama"]

[texiv.chunk]
stopwords_path = ""

[texiv.similarity]
MTHD = "cosine"

[texiv.filter]
VALVE_TYPE = "value"
valve = 0.618
```

---

## 📊 Methods / 方法

### 1. texiv_it() - Single Text Processing / 单文本处理

**English:** Process a single text with keywords
**中文:** 使用关键词处理单个文本

```python
# English
text = "China's digital economy has grown rapidly in recent years."
keywords = ["digital", "economy", "China"]
result = texiv.texiv_it(text, keywords)

# 中文
text = "近年来中国数字经济发展迅速。"
keywords = ["数字", "经济", "中国"]
result = texiv.texiv_it(text, keywords)
```

### 2. texiv_df() - DataFrame Processing / DataFrame处理

**English:** Process a pandas DataFrame column
**中文:** 处理pandas DataFrame列

```python
import pandas as pd

# English
df = pd.DataFrame({
    'text': ["First document", "Second document", "Third document"]
})
keywords = ["document", "text"]
result_df = texiv.texiv_df(df, 'text', keywords)

# 中文
df = pd.DataFrame({
    'text': ["第一个文档", "第二个文档", "第三个文档"]
})
keywords = ["文档", "文本"]
result_df = texiv.texiv_df(df, 'text', keywords)
```

### 3. texiv_stata() - Stata Integration / Stata集成

**English:** Process multiple texts for Stata integration
**中文:** 处理多个文本用于Stata集成

```python
texts = ["Text 1", "Text 2", "Text 3"]
keywords = "key1 key2 key3"
freqs, counts, rates = texiv.texiv_stata(texts, keywords)
```

---

## ⚙️ Advanced Configuration / 高级配置

### Stopwords Customization / 停用词定制

**English:** Use custom stopwords
**中文:** 使用自定义停用词

```python
# English
custom_stopwords = ["the", "and", "or"]
result = texiv.texiv_it(text, keywords, stopwords=custom_stopwords)

# 中文
custom_stopwords = ["的", "了", "和"]
result = texiv.texiv_it(text, keywords, stopwords=custom_stopwords)
```

### Threshold Adjustment / 阈值调整

**English:** Adjust similarity threshold
**中文:** 调整相似度阈值

```python
# English - Set custom threshold
texiv = TexIV(valve=0.75)  # 75% similarity threshold

# 中文 - 设置自定义阈值
texiv = TexIV(valve=0.75)  # 75%相似度阈值
```

---

## 🚀 Command Line Usage / 命令行使用

**English:** After installation, use the command line tool:
**中文:** 安装后，可以使用命令行工具：

```bash
# View help
texiv --help

# Initialize configuration
texiv --init

# Process file
texiv --file input.txt --keywords "keyword1,keyword2"
```

---

## 📋 Output Interpretation / 输出解释

### Result Format / 结果格式

```python
{
  "freq": 5,     # Number of relevant segments / 相关片段数量
  "count": 12,   # Total segments analyzed / 分析的总片段数
  "rate": 0.4167 # Relevance ratio (freq/count) / 相关比例
}
```

### Interpretation Guidelines / 解释指南

**English:**
- **freq**: Higher values indicate more relevant content
- **count**: Total number of text segments analyzed
- **rate**: Ratio between 0-1, higher means more keyword relevance

**中文:**
- **freq**: 数值越高表示相关内容越多
- **count**: 分析的总文本片段数量
- **rate**: 0-1之间的比例，越高表示关键词相关性越强

---

## 🛠️ Troubleshooting / 故障排除

### Common Issues / 常见问题

**English:**
1. **API Key Error**: Ensure your API key is valid in config.toml
2. **Network Issues**: Check internet connection and API endpoints
3. **Memory Issues**: Reduce MAX_LENGTH for large texts

**中文:**
1. **API密钥错误**: 确保config.toml中的API密钥有效
2. **网络问题**: 检查网络连接和API端点
3. **内存问题**: 对大文本减少MAX_LENGTH值

### Debug Mode / 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# English
texiv = TexIV()
texiv.texiv_it(text, keywords)

# 中文
texiv = TexIV()
texiv.texiv_it(text, keywords)
```

---

## 📚 Examples / 示例

### Research Application / 研究应用

**English:** Economics research example
**中文:** 经济学研究示例

```python
# English - Policy analysis
policies = [
    "The digital transformation policy promotes innovation...",
    "Environmental regulations impact business operations...",
    "Trade policies affect international competitiveness..."
]
keywords = ["digital", "innovation", "policy"]

# 中文 - 政策分析
policies = [
    "数字化转型政策促进了创新发展...",
    "环境监管影响了企业运营...",
    "贸易政策影响了国际竞争力..."
]
keywords = ["数字化", "创新", "政策"]

# Process all policies / 处理所有政策
results = [texiv.texiv_it(policy, keywords) for policy in policies]
```

### Batch Processing / 批量处理

```python
# English
import pandas as pd

df = pd.read_csv("research_data.csv")
keywords = ["technology", "innovation", "digital"]
result_df = texiv.texiv_df(df, "abstract", keywords)
result_df.to_csv("processed_data.csv", index=False)

# 中文
import pandas as pd

df = pd.read_csv("研究数据.csv")
keywords = ["技术", "创新", "数字化"]
result_df = texiv.texiv_df(df, "abstract", keywords)
result_df.to_csv("处理后数据.csv", index=False)
```

---

## 📞 Support / 支持

**English:**
- GitHub Issues: https://github.com/sepinetam/texiv/issues
- Documentation: https://github.com/sepinetam/texiv/wiki
- Email: sepinetam@gmail.com

**中文:**
- GitHub问题: https://github.com/sepinetam/texiv/issues
- 文档: https://github.com/sepinetam/texiv/wiki
- 邮箱: sepinetam@gmail.com

---

**Author:** Claude Code (@Kimi)  
**Version:** 0.1.8  
**Last Updated:** 2025-07-15  
**文档版本:** 1.0