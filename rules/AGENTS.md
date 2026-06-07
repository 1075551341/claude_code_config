---
trigger: model_decision
description: 多 Agent 协作与互斥规则。触发：并行 Agent、子代理、任务编排。
---

# Agent 协作规则

> 归属矩阵 → `MANIFEST.yaml` | 核心 8 个 → `agents/README.md`

## 核心 8

planner | code-explorer | code-reviewer | build-error-resolver | architect | spec-reviewer | context-manager | agentic-orchestrator

## gstack 审查 5 + 补全 7

审查（skeleton）：eng-reviewer | ceo-reviewer | designer | qa | security-reviewer

补全（supplement）：cso | sre | release-engineer | product-manager | design-engineer | performance-engineer | doc-writer

位置：`agents/` + `catalog/agents/`（按需复制）

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
| 设计探索(多方案) | design-shotgun（gstack v0.19） |
| 一键部署 | land-and-deploy（gstack v0.19） |
| 多Agent浏览器 | pair-agent（gstack v0.19） |
| 跨模型验证 | codex-reviewer（gstack /codex） |
| iOS 变更 | ios-specialist（gstack v0.19） |
| 外部编排 | deer-flow (flash/standard/pro/ultra) |
| 任务追踪 | task-master MCP（按需） |

## 审查路由规则

```
所有变更        → eng-reviewer (必须)
产品/新功能     → + ceo-reviewer
UI/UX 变更      → + designer + design-shotgun(多方案探索,gstack v0.19)
安全敏感变更    → + security-reviewer + cso(OWASP+STRIDE)
iOS 变更        → + ios-specialist (gstack v0.19)
infra/配置      → CEO Review 可跳过
跨模型验证      → + codex-reviewer (gstack /codex)
部署/发布       → + land-and-deploy (gstack v0.19)
```

## 禁止（防互博）

- agent 间共享可变状态（包括全局变量/文件锁/环境变量隐式共享）
- planner 与 agentic-orchestrator 同时编排同一任务
- hook/pre-task-planner 替代 skill/writing-plans
- context-manager 重复 claude-mem 存储逻辑
- 同一制品路径并行写入（DAG冲突检测阻断）
- 子agent 回写主会话上下文（仅通过三态制品通信）
- 按 agent 名称堆叠委派（应按 MANIFEST concern→owner 路由）

## 上下文预算

主 agent <40%（编排） | subagent 30%（实现） | 传递最小必要数据
70% 择机压缩 | 90% 强制压缩或新 subagent

## 持续学习

失败模式 → `experiences/rejected/` | 成功模式 → `experiences/patterns/` | hook/stop-pattern-extraction

## 委派原则（ruflo 吸收）

> **source**: ruvnet/ruflo — 参考排除

- 按 MANIFEST concern→owner 路由，禁止并行多 orchestrator
- 按能力委派（探索/计划/审查/执行），非按 agent 名称堆叠
