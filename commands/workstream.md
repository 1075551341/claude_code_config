---
description: 并行任务流管理（git worktree 隔离，GSD workstreams）
---

# /workstream — 并行任务流

> **正文在 skill/workstream-management**。本命令触发该 skill。

## 子命令

| 命令 | 作用 |
|------|------|
| `/workstream new <name>` | 创建 worktree + `.planning/phases/<name>/` |
| `/workstream status` | 活跃流状态 |
| `/workstream list` | 全部流（含已完成） |
| `/workstream merge <name>` | 合并 + claude-mem 整合 |

## 门控

合并前 `verification-before-completion` + `eng-reviewer` 通过。
