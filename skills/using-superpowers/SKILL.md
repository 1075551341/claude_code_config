---
name: using-superpowers
description: 技能发现与 Tool-First 路由。触发：会话开始、不确定用什么技能、开始任务。
layer: skeleton
source: obra/superpowers
---

# 技能发现与 Tool-First

## 铁律

> 1% 可能适用 → 必须先查 skill，禁止即兴替代工作流。

## 调用链（顺序固定）

```
MANIFEST.yaml → P0 skill(5) → 全局 skill(29) → catalog/skills → agent → MCP/hook
```

## P0（强制 5）

| 信号 | Skill |
|------|-------|
| 会话开始/不确定 | using-superpowers（本 skill） |
| 方案/架构/选型 | brainstorming |
| 任何修改/变更 | change-impact-analysis |
| 完成/验收 | verification-before-completion |
| 调试/报错 | systematic-debugging |

## 工作流扩展

| 信号 | Skill / Agent |
|------|---------------|
| 写计划 | writing-plans → agent/planner |
| 执行计划 | executing-plans |
| TDD | test-driven-development |
| 代码审查 | requesting/receiving-code-review → agent/code-reviewer |
| 并行子任务 | subagent-driven-development → agent/agentic-orchestrator |
| 上下文压缩 | memory-compression → agent/context-manager |
| 输出冗长 | caveman-compress |

## 领域能力

不在全局 17 个内 → `catalog/skills/`（migrate-from-legacy.py 按需复制）

## Token

- Shell：`hook/pre-rtk-rewrite`（RTK）
- 回复：`skill/caveman-compress`

## 原则

不跳过、不替代、不省略 skill 步骤；Iron Law 不可违反。
