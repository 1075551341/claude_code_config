---
description: 设计方案与原子任务分解（②规格阶段，触发 writing-plans）
---

# /plan — 设计方案与任务分解

> **正文在 skill/writing-plans**。本命令仅触发该 skill；复杂计划可委派 agent/planner。

## 触发

1. 加载 `skills/writing-plans/SKILL.md`
2. 非简单任务须先完成 brainstorming 且用户批准设计（HARD-GATE）

## 规格轨道（三选一，互斥）

| 场景 | 产出路径 |
|------|----------|
| 功能变更 | `openspec/changes/<id>/`（/propose） |
| 大功能多阶段 | `.planning/phases/` |
| 小功能 | `spec/<project>/` |

<!-- spine:stage-gate -->
## 门控（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）

- 阶段：②规格 | skill：`skills/writing-plans/SKILL.md` | 角色：planner（frontier / high）
- 进入：设计已批准
- 退出（全部满足才进入下一阶段）：
  - spec-validation 通过，无静默缩 scope
  - 就绪定义（quality.definition_of_ready）全部满足
<!-- /spine:stage-gate -->
