---
description: 多 Agent 协作与互斥规则。触发：并行 Agent、子代理、任务编排。
alwaysApply: false
---

# Agent 协作规则

> 归属矩阵 → `MANIFEST.yaml` | 核心 8 个 → `agents/README.md`

## 核心 8

planner | code-explorer | code-reviewer | build-error-resolver | architect | spec-reviewer | context-manager | agentic-orchestrator

## gstack 审查角色（catalog/agents/）

eng-reviewer | ceo-reviewer | designer | qa | security

## 何时委派

| 条件 | Agent |
|------|-------|
| 只读探索 | code-explorer |
| 写计划 | planner（→ writing-plans skill） |
| 多模块并行 | agentic-orchestrator |
| 构建失败 | build-error-resolver |
| spec 审查 | spec-reviewer |
| 代码审查 | code-reviewer + eng-reviewer |
| 产品决策 | ceo-reviewer |
| UI/UX 审查 | designer |
| 测试审查 | qa |
| 安全审计 | security |

## 审查路由规则

```
所有变更        → eng-reviewer (必须)
产品/新功能     → + ceo-reviewer
UI/UX 变更      → + designer
安全敏感变更    → + security
infra/配置      → CEO Review 可跳过
```

## 禁止（防互博）

- agent 间共享可变状态
- planner 与 agentic-orchestrator 同时编排同一任务
- hook/pre-task-planner 替代 skill/writing-plans
- context-manager 重复 claude-mem 存储逻辑

## 上下文预算

主 agent <40%（编排） | subagent 30%（实现） | 传递最小必要数据
50% compact | 70% 强制压缩或新 subagent

## 持续学习

失败模式 → `experiences/rejected/` | 成功模式 → `experiences/patterns/` | hook/stop-pattern-extraction
