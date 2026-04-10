---
name: github
description: 使用gh命令管理GitHub仓库的Issue、PR、CI/CD等。触发词：GitHub CLI、gh命令、Issue管理、PR管理、GitHub自动化。
---

# GitHub CLI

## 核心功能

- Issue创建和管理
- Pull Request操作
- CI/CD状态查看
- 仓库管理
- Actions工作流

## 常用命令

```bash
# 创建Issue
gh issue create --title "标题" --body "描述"

# 创建PR
gh pr create --title "标题" --body "描述"

# 查看CI状态
gh run list

# 仓库操作
gh repo create my-repo --public
```

## 使用场景

- 自动化工作流
- 批量Issue处理
- PR模板管理
- CI/CD集成
