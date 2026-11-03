# Agents 智能体库

> **全局 9 个**（2 阶段角色 + 7 独立审查者）+ **catalog/agents/** 领域库（按需复制）。
>
> agent 不声明 `model` / `effort`：一律继承调用方（会话模型、编辑器选择、Task 传参）。`workflow.py check` 的 lint 拦截任何 model/effort 键。

完整索引 → [agents-INDEX.md](../agents-INDEX.md) | 审查路由 → `rules/AGENTS.md`（派生自 `config/workflow.yaml`）

## 阶段角色 2

planner（②规格）| change-implementer（③执行 + 落实审查清单）

## 独立审查者 7（只找问题，不改文件；PASS 是任务完成的必要条件）

eng-reviewer（必审）| ceo-reviewer | designer | dx-reviewer | qa | security-reviewer | cross-model-reviewer

## v13 去向

| 原 agent | 去向 |
| --- | --- |
| code-explorer | 编辑器内置 explore 子代理 + `codegraph_explore`（R17） |
| architect | `skills/brainstorming`（设计）+ planner（计划） |
| agentic-orchestrator | 主会话 + `skills/subagent-driven-development` |
| build-error-resolver | change-implementer + `skills/systematic-debugging` |
| spec-reviewer | `skills/spec-validation`（②规格 exit） |
| sre / doc-writer | `skills/ship`；文档同步是 R20「漏改」维的一部分 |
| 原跨模型审查者（v12 名含厂商） | 更名 `cross-model-reviewer`，去厂商化（调用方选不同模型） |

## 委派原则

- 子 Agent fresh context（R12）；制品通信，禁止共享可变状态
- 审查者与修改者不得为同一 agent；每轮审查全新派发，禁止 resume
- `context-manager` 已合并至 claude-mem；勿重复注册
