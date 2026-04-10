---
name: outline
description: Outline文档管理，包括搜索、创建、编辑文档。触发词：Outline、outline文档、wiki管理、文档协作。
---

# Outline 文档管理

## 功能

- 搜索和阅读Outline文档
- 创建新文档
- 编辑现有文档
- 管理文档结构

## API集成

使用Outline API进行文档操作：
```bash
# 获取文档列表
GET /api/documents

# 创建文档
POST /api/documents
{
  "title": "文档标题",
  "content": "文档内容"
}

# 更新文档
PUT /api/documents/:id
```

## 使用场景

- 知识库管理
- 团队文档协作
- 技术文档维护
- 项目文档管理

## 配置

需要配置：
- Outline实例URL
- API密钥
- 工作空间ID
