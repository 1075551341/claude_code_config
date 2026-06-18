---
description: 创建 OpenSpec 规格提案（②规格阶段）
---

# /propose（别名: /spec）— 创建规格提案

> **core CLI**：优先 `openspec` `/opsx:propose`；无 CLI 时按下列手动手册。
> 安装：`npm i -g @fission-ai/openspec@latest` → `openspec init --tools cursor`（v1.4.1 无 expanded preset）

基于 OpenSpec 模式，为新功能/变更创建规格提案。

## 输出

在 `openspec/changes/CHANGE_NAME/` 下创建：

```
openspec/changes/CHANGE_NAME/
├── proposal.md   # 为什么要做、改什么、影响范围
├── specs/        # 需求规格与场景
├── design.md     # 技术方案（可选）
└── tasks.md      # 实现任务清单
```

## proposal.md 模板

```markdown
# [变更名称]

## Why

[1-2 句说明动机]

## What Changes

- [变更点 1]
- [变更点 2]

## Impact

- 影响范围: [模块/文件]
- 破坏性变更: 是/否
- 依赖: [新增/移除的依赖]
```

## 门控

- 提案已获用户批准 ✓
- 验收标准明确 ✓
