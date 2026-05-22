---
description: 多 Agent 协作与互斥规则。触发：并行 Agent、子代理、任务编排。
alwaysApply: false
---

# Agent 协作规则

> 归属矩阵 → `MANIFEST.yaml` | 核心 8 个 → `agents/README.md`

## 核心 8

planner | code-explorer | code-reviewer | build-error-resolver | architect | spec-reviewer | context-manager | agentic-orchestrator

## 何时委派

| 条件 | Agent |
|------|-------|
| 只读探索 | code-explorer |
| 写计划 | planner（→ writing-plans skill） |
| 多模块并行 | agentic-orchestrator |
| 构建失败 | build-error-resolver |
| spec 审查 | spec-reviewer |

## 禁止（防互博）

- agent 间共享可变状态
- planner 与 agentic-orchestrator 同时编排同一任务
- hook/pre-task-planner 替代 skill/writing-plans
- context-manager 重复 claude-mem 存储逻辑

## 上下文预算

主 agent 60% | subagent 30% | 传递最小必要数据

## 持续学习

失败模式 → `experiences/rejected/` | 成功模式 → `experiences/patterns/` | hook/stop-pattern-extraction
