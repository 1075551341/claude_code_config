---
description: 创建 OpenSpec 规格提案（②规格阶段）
---

# /propose（别名: /spec）— 创建规格提案

> **core CLI**：优先 `openspec` `/opsx:propose`；无 CLI 时按 `rules/OPENSPEC.md`（四大制品/命令链/约束 SSOT）手动创建 `openspec/changes/<id>/`（v11.1 薄壳化：目录结构不复写）。
> 安装：`npm i -g @fission-ai/openspec@latest` → `openspec init --tools cursor`（v1.4.1 无 expanded preset）

## proposal.md 模板（本命令独有内容）

```markdown
# [变更名称]

## Why
[1-2 句说明动机]

## What Changes
- [变更点 1]
- [变更点 2]

## Impact
影响范围: [模块/文件] | 破坏性变更: 是/否 | 依赖: [新增/移除的依赖]
```

## 门控

- 提案已获用户批准 ✓
- 验收标准明确 ✓
