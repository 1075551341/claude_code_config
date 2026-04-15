---
name: article-extractor
description: 从网页提取完整文章内容和元数据
triggers: [文章提取, 网页文章, article extractor, 网页内容提取]
---

# 文章提取

## 功能

从网页URL提取完整文章内容，包括：

- 标题
- 正文内容
- 作者信息
- 发布时间
- 元数据

## 使用场景

- 研究和资料收集
- 内容分析
- 文章归档
- 内容摘要生成

## 实现方式

使用Web抓取工具（如BeautifulSoup、newspaper3k）解析HTML，提取文章主体内容

## 输出格式

```markdown
# [文章标题]

**作者**：[作者名]
**发布时间**：[日期]
**来源**：[URL]

## 正文

[文章内容]
```
