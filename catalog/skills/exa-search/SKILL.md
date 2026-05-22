---
name: exa-search
description: 使用 Exa AI 进行语义搜索和智能检索
triggers: [使用 Exa AI 进行语义搜索和智能检索]
---

# Exa AI 搜索

## 核心功能

```
🔍 语义搜索 - 基于含义而非关键词的搜索
🌐 网页搜索 - 实时检索高质量网页内容
📄 内容提取 - 智能提取网页正文
📊 相似内容 - 查找语义相似的网页
```

## API 配置

```bash
EXA_API_KEY=your-exa-api-key
```

## 基础用法

### Python SDK

```python
from exa_py import Exa

exa = Exa(api_key="your-api-key")

# 语义搜索
results = exa.search_and_contents(
    "best practices for React performance optimization",
    use_autoprompt=True,
    type="auto",
    num_results=10,
    contents={
        "text": { "max_characters": 1000 },
        "livecrawl": "always"
    }
)

for result in results.results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Summary: {result.text[:200]}...")
    print("---")
```

### TypeScript/Node.js

```typescript
import Exa from 'exa-js';

const exa = new Exa('your-api-key');

// 搜索并提取内容
const results = await exa.searchAndContents('machine learning tutorials', {
  numResults: 5,
  useAutoprompt: true,
  text: { maxCharacters: 2000 },
});

// 结果处理
results.results.forEach((result) => {
  console.log(`${result.title}\n${result.url}\n`);
});
```

## 高级搜索

### 按域名过滤

```python
results = exa.search_and_contents(
    "React hooks tutorial",
    include_domains=["react.dev", "github.com"],
    num_results=10,
)
```

### 排除域名

```python
results = exa.search_and_contents(
    "JavaScript best practices",
    exclude_domains=["w3schools.com"],
    num_results=10,
)
```

### 按日期过滤

```python
from datetime import datetime, timedelta

results = exa.search_and_contents(
    "latest AI news",
    start_published_date=datetime.now() - timedelta(days=7),
    num_results=10,
)
```

### 指定内容类型

```python
results = exa.search_and_contents(
    "API documentation",
    type="keyword",  # 或 "neural", "auto"
    category="company",  # company, research paper, github, tweet, movie, song, book
    num_results=10,
)
```

## 内容提取

### 提取结构化数据

```python
results = exa.search_and_contents(
    "Python data analysis libraries",
    num_results=5,
    contents={
        "text": {"max_characters": 2000},
        "summary": True,
    }
)

for result in results.results:
    print(f"Summary: {result.summary}")
```

### 实时爬取

```python
results = exa.search_and_contents(
    "breaking news today",
    num_results=5,
    livecrawl="always",  # 强制实时爬取
    contents={
        "text": True,
    }
)
```

## 相似内容查找

```python
# 基于URL查找相似内容
similar = exa.find_similar_and_contents(
    "https://react.dev/learn",
    num_results=5,
    contents={
        "text": {"max_characters": 1000}
    }
)
```

## 与 AI 工作流集成

### RAG 系统集成

```python
from openai import OpenAI

openai = OpenAI()

def search_and_summarize(query: str) -> str:
    # 1. Exa 搜索
    results = exa.search_and_contents(
        query,
        num_results=5,
        contents={"text": {"max_characters": 2000}}
    )

    # 2. 构建上下文
    context = "\n\n".join([
        f"Source: {r.url}\n{r.text}"
        for r in results.results
    ])

    # 3. LLM 总结
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "基于搜索结果回答问题"},
            {"role": "user", "content": f"问题: {query}\n\n参考资料:\n{context}"}
        ]
    )

    return response.choices[0].message.content
```

### 批量搜索

```python
queries = [
    "React performance optimization",
    "Vue 3 composition API",
    "Angular signals",
]

all_results = []
for query in queries:
    results = exa.search_and_contents(query, num_results=3)
    all_results.extend(results.results)
```

## 最佳实践

```markdown
1. 使用 autoprompt 自动优化搜索词
2. 合理设置 max_characters 避免处理过多内容
3. 使用 include_domains 提高结果质量
4. 批量请求时注意 API 限制
5. 缓存常用查询结果
```