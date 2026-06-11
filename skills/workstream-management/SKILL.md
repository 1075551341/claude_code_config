---
name: workstream-management
description: GSD 并行任务流管理。触发词：并行任务、workstream、多任务同时、工作流。
triggers: [并行任务, workstream, 多任务, 工作流, git worktree]
layer: supplement
source: open-gsd/gsd-core
disable-model-invocation: true
loading_tier: L3
---

# Workstream 并行任务流

基于 git worktrees 的并行开发隔离，对齐 GSD v1.42.3 workstreams。

## 触发

- 需同时推进 2+ 个独立任务
- 关键词：并行、workstream、多分支并行

## 命令

| 命令 | 作用 |
|------|------|
| `/workstream new <name>` | `git worktree add` + `.planning/phases/<name>/` |
| `/workstream status` | 列出活跃流状态 |
| `/workstream list` | 所有流（含已完成） |
| `/workstream merge <name>` | PR 合并 + claude-mem 整合记忆 |

## 流程

```
1. /workstream new feature-a
   → git worktree add ../ws-feature-a -b ws/feature-a
   → mkdir .planning/phases/feature-a/{STATE.md,tasks.md}

2. 各 workstream 独立分支 + 独立 claude-mem platform_source

3. /workstream merge feature-a
   → verification-before-completion
   → PR → 合并后 claude-mem 记忆整合
```

## 约束

- 每个 workstream 独立 git branch
- 同一制品路径禁止并行写入（R12）
- 合并前必须 eng-reviewer + verification-before-completion
- 详见 `skill/using-git-worktrees`

## 与规格三轨

| 场景 | 轨道 |
|------|------|
| 单流大功能 | GSD `.planning/phases/` |
| 多流并行 | workstreams + `.planning/phases/<name>/` |
| brownfield 变更 | OpenSpec `openspec/changes/<id>/` |
