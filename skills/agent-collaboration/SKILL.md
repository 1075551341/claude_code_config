---
name: agent-collaboration
description: 多 Agent 协作与互斥。触发：并行 Agent、子代理、任务编排。
triggers: [并行 Agent, 子代理, 任务编排, 互斥]
layer: supplement
source: local
loading_tier: L3
disable-model-invocation: true
---

# Agent 协作规则

> 归属矩阵 → `MANIFEST.yaml` | 核心 7 个 → `agents/README.md`

## 核心

planner | build-error-resolver | spec-reviewer | agentic-orchestrator | change-implementer | explore

> 跨会话记忆 → claude-mem

## gstack 审查 + 跨模型

审查：eng-reviewer | ceo-reviewer | designer | dx-reviewer | qa | security-reviewer  
跨模型：codex-reviewer

位置：`agents/`（计数见 MANIFEST）。v12 已删 architect / sre / doc-writer / code-explorer；code-reviewer 并入 eng-reviewer。

> v12：低频变体 land-and-deploy / design-shotgun 在 `agents/`（disable-model-invocation）。

位置：`agents/`（计数见 MANIFEST）

## 何时委派

| 条件 | Agent |
|------|-------|
| 只读探索 | codegraph_explore / explore |
| 写计划 | planner（→ writing-plans skill） |
| 多模块并行 | agentic-orchestrator |
| 构建失败 | build-error-resolver |
| spec 审查 | spec-reviewer |
| 代码审查 | eng-reviewer（只找问题，禁止改文件） |
| 落实修改 | 审查未满足项 | change-implementer（禁止审查） |
| 产品决策 | ceo-reviewer |
| UI/UX 审查 | designer + dx-reviewer |
| DX 体验审查 | dx-reviewer |
| 测试审查 | qa |
| 安全审计（增量/全量） | security-reviewer（深度模式=原 cso） |
| 跨模型验证 | codex-reviewer（gstack /codex） |
| 设计探索/部署 | agents/design-shotgun、land-and-deploy（disable-model-invocation） |
| 外部编排 | deer-flow (flash/standard/pro/ultra) |
| 任务追踪 | task-master MCP（按需） |

## 审查路由规则

```
所有变更        → eng-reviewer（只找问题；修复 → change-implementer）
产品/新功能     → + ceo-reviewer
UI/UX 变更      → + designer + dx-reviewer（多方案探索按需启用 design-shotgun）
DX体验变更      → + dx-reviewer
安全敏感变更    → + security-reviewer（全量审计走其深度模式=原cso OWASP+STRIDE）
infra/配置      → CEO Review 可跳过
跨模型验证      → + codex-reviewer (gstack /codex)
部署/发布       → skill/ship（完整闭环按需启用 land-and-deploy）
```

## 禁止（防互博）

- agent 间共享可变状态（包括全局变量/文件锁/环境变量隐式共享）
- planner 与 agentic-orchestrator 同时编排同一任务
- hook/pre-task-planner 替代 skill/writing-plans
- 勿恢复 agent/context-manager（已合并 claude-mem）
- 同一制品路径并行写入（DAG冲突检测阻断）
- 子agent 回写主会话上下文（仅通过三态制品通信）
- 按 agent 名称堆叠委派（应按 MANIFEST concern→owner 路由）
- 审查者与修改者同一 agent（禁止既审又改；审查只找问题，修改必须 change-implementer）
- `resume` 上一轮审查者充当本轮独立审查（须全新 Task/Agent；上轮遗漏不得继承为已扫范围）

## 上下文预算

主 agent <40%（编排） | subagent 30%（实现） | 传递最小必要数据
70% 择机压缩 | 90% 强制压缩或新 subagent

## 持续学习

失败/成功模式 → claude-mem observation（R18 记忆柱统一承接；原 `experiences/` 文件体系已归档至 `docs/archive/experiences/`）

## 委派原则（ruflo 吸收）

> **source**: ruvnet/ruflo — 参考排除

- 按 MANIFEST concern→owner 路由，禁止并行多 orchestrator
- 按能力委派（探索/计划/审查/执行），非按 agent 名称堆叠
