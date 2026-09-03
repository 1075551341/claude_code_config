---
name: using-superpowers
description: 技能发现与 Tool-First 路由。触发：会话开始、不确定用什么技能、开始任务。
triggers: [会话开始, 技能路由, 开始任务, 不确定用什么技能]
layer: skeleton
source: obra/superpowers
loading_tier: L1
---

# 技能发现与 Tool-First

## 铁律

> 1% 可能适用 → 必须先查 skill，禁止即兴替代工作流。

## 显式调用（Cursor / Claude Code 通用）

| 方式          | 用法                                   | 适用                     |
| ------------- | -------------------------------------- | ------------------------ |
| **Read 工具** | `Read skills/<name>/SKILL.md`          | **首选**；L2/L3 必须     |
| slash 命令    | `/discuss` `/plan` `/deep-research` 等 | 入口快捷；仍应 Read 全文 |
| 关键词        | description/triggers 匹配              | 路由信号；触发后 Read    |
| Task 子代理   | `subagent_type` + 任务描述             | L3 agents                |

L2/L3 设 `disable-model-invocation: true` → 不会自动注入上下文；**进入阶段时必须显式 Read**。

## 加载等级（L0–L3）

| 等级 | 机制                                                            |
| ---- | --------------------------------------------------------------- |
| L0   | CLAUDE.md（含路由，v11 并入 ROUTER）+ CORE alwaysApply          |
| L1   | 本 skill + task-triage + change-impact-analysis + brainstorming |
| L2   | 进入阶段 Read 全文（→ scenario-router.yaml + OPENSPEC.md） |
| L3   | slash/关键词后 Read 其余 skill / agent / MCP / claude-mem       |

> ROUTER/CLAUDE.md 以 **L0–L3** 为准；历史 L4（agents/MCP/claude-mem）已并入 L3（MANIFEST `L3_dispatch`）。

同会话同一 skill 已 Read → 不重复 Read（制品 hash 变更除外）。

## Per-harness 工具映射（superpowers v6 references）

v6.0.0 起 superpowers 用 vendor-neutral 工具名 + `references/` 目录映射各 harness（Claude Code / Codex / Copilot / Gemini / Pi / Antigravity）。本地落地：Cursor 用 Read/Glob/Grep/Task；Claude Code 用对应原生工具。**禁止凭记忆套用某 harness 的专有工具名**（如在 Cursor 误调 Claude Code 专属命令）。

## 任务分类

分类树/六维/升档触发 SSOT → `skills/task-triage/SKILL.md`。入口：R18 claude-mem search（相关先查）→ Read task-triage（Phase0 盘点）→ **查 `config/scenario-router.yaml` 对应场景** → 显式 Read `load.skills/agents/rules` → 工具经 `config/harness-capabilities.yaml` 按当前 harness 解析 capability（缺则 fallback/interrupt，禁止假装已调用）。**简单旁路**仅 attempt=1（不 Read executing-plans/subagent-driven-development），完成前仍须 Read verification-before-completion。

## P0 / L2 / 规格三轨

判定 SSOT → `skills/task-triage/SKILL.md`。分类后必加载 → `config/scenario-router.yaml`。规格三轨 → `rules/OPENSPEC.md`。调研三档 → `research_l1|l2|l3`（官方分类调研类=L3）。禁止在本文件复制场景→工具表。

## 调用链

```
task-triage → config/scenario-router.yaml → Read load.* → harness-capabilities 解析 capability
```

独立审查前必须双图 ensure。并行审查仅当只读 + 维度不重叠 + Task `model=inherit`（禁止倍率档）。

## 工作流扩展（L3 信号触发）

| 信号     | Skill                                                           |
| -------- | --------------------------------------------------------------- |
| 写计划   | writing-plans                                                   |
| TDD      | test-driven-development (默认关闭,用户显式要求时触发)           |
| 代码审查 | requesting-code-review → eng-reviewer                           |
| 架构决策 | adr-management                                                  |
| 长时自主 | catalog/skills/claude-to-deerflow（v11 降级 catalog，按需复制） |
| Git 提交 | git-workflow                                                    |
| 开 PR    | pr-workflow                                                     |
| 输出冗长 | caveman-compress                                                |

## Token

- Shell：`hook/pre-rtk-rewrite`
- 回复：`skill/caveman-compress`

## 原则

不跳过、不替代、不省略 skill 步骤。
