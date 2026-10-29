---
trigger: model_decision
description: 多 Agent 协作、独立审查派发与互斥规则。触发：并行 Agent、子代理、任务编排、审查派发。
---

# Agent 协作规则

> 清单 → `agents/README.md` | 阶段/完成定义/审查 → `config/workflow.yaml` | 归属 → `MANIFEST.yaml`

## 何时委派

| 条件 | Agent |
|------|-------|
| 写计划 | planner（→ writing-plans skill） |
| 落实修改 / 审查未满足项 | change-implementer（只改不审） |
| 每个任务的独立审查 | eng-reviewer（必审）+ 下方路由 |
| 只读探索 / 多模块并行 / 构建失败 | 主会话（编辑器内置 explore 子代理、subagent-driven-development、systematic-debugging） |
| 领域专家 | catalog/agents/（按需复制进项目） |

## 审查路由

<!-- spine:review-routing -->
```
always       → eng-reviewer
product      → + ceo-reviewer
ui           → + designer, dx-reviewer
api_dx       → + dx-reviewer
tests        → + qa
security     → + security-reviewer
cross_model  → + cross-model-reviewer
```

> 派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改。审查者模型由调用方选择；cross_model 组要求与实现者不同的模型。
<!-- /spine:review-routing -->

## 执行并发

<!-- spine:concurrency -->
**执行并发**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：无依赖且可后台的命令/操作不得阻塞会话，优先并行。有依赖或下一步需要其输出的仍按序、禁止后台。长驻服务器 / watcher 保持后台。不是第三道 PASS 门，不另建 Stop hook，不改 `browser_ui_tests`。

- 无依赖且可后台的命令/操作不得阻塞会话，优先并行
- 有依赖或下一步需要其输出的步骤仍按序执行，禁止后台
- 长驻服务器 / watcher 保持后台
<!-- /spine:concurrency -->

infra/配置变更可跳过 product 组；eng-reviewer 永不跳过。

**一轮 = 改 → 验 → 审查前刷图一次 → 本批全新七维审查。** 无依赖的审查者同一条消息并行 `Task`；刷一次图再 fan-out。批次内任一 `NEEDS-CHANGES` / 七维缺项 / 不干净 PASS → 整轮不通过：主会话合并完整清单，派**一次** `change-implementer` 集中改齐，再全新派审。审查 prompt 写明：原始要求、本轮已刷新、使用 CRG `get_impact_radius` / `get_review_context`（有图）+ `codegraph_explore` blast-radius。

## 模型选择（不在本包）

- 派发子 Agent 时由**调用方**决定模型与推理强度（编辑器 Task 参数、会话设置、harness 默认）；本包任何文件都不指定。
- `cross_model` 组：调用方选一个与实现者不同的模型运行 cross-model-reviewer；选不出就不派。

## 禁止（防互博）

- agent 间共享可变状态（全局变量/文件锁/环境变量隐式共享）；同一制品路径并行写入
- 子 agent 回写主会话上下文（仅通过制品通信）
- 审查者与修改者同一 agent；审查者改文件或贴补丁
- `resume` 上一轮审查者充当本轮独立审查（须全新 Task；上轮清单不得限定本轮范围）
- 以自检 / 实现者自签 / 验证命令全绿代替独立审查 PASS
- 勿恢复 agent/context-manager（已合并 claude-mem）

## 上下文预算

主 agent 编排、subagent 实现；传递最小必要数据。阈值 → `rules/CORE.md`。
