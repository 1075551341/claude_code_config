---
name: using-superpowers
description: 技能发现与 Tool-First 路由。触发：会话开始、不确定用什么技能、开始任务。
layer: skeleton
source: obra/superpowers
loading_tier: L1
---

# 技能发现与 Tool-First

## 铁律

> 1% 可能适用 → 必须先查 skill，禁止即兴替代工作流。

## 显式调用（Cursor / Claude Code 通用）

| 方式 | 用法 | 适用 |
|------|------|------|
| **Read 工具** | `Read skills/<name>/SKILL.md` | **首选**；L2/L3 必须 |
| slash 命令 | `/discuss` `/plan` `/deep-research` 等 | 入口快捷；仍应 Read 全文 |
| 关键词 | description/triggers 匹配 | 路由信号；触发后 Read |
| Task 子代理 | `subagent_type` + 任务描述 | L4 agents |

L2/L3 设 `disable-model-invocation: true` → 不会自动注入上下文；**进入阶段时必须显式 Read**。

## 加载等级（L0–L3，CLAUDE.md 细分 L4）

| 等级 | 机制 |
|------|------|
| L0 | CLAUDE-ROUTER + CLAUDE + CORE alwaysApply |
| L1 | 本 skill + change-impact-analysis 常驻 |
| L2 | 进入阶段 Read 全文（见下表） |
| L3 | slash/关键词后 Read supplement skill / agent / MCP / claude-mem |

> **统一口径**：ROUTER（L0 always）以 **L0–L3** 为准，L3 = 其余 skills/rules/agents/MCP/claude-mem。CLAUDE.md 出于细分把 agents(Task)/MCP/claude-mem 单列为 **L4**，等价于 ROUTER 的 L3 子集。本 skill 采用 ROUTER 口径。

同会话同一 skill 已 Read → 不重复 Read（制品 hash 变更除外）。

## Per-harness 工具映射（superpowers v6 references）

v6.0.0 起 superpowers 用 vendor-neutral 工具名 + `references/` 目录映射各 harness（Claude Code / Codex / Copilot / Gemini / Pi / Antigravity）。本地落地：Cursor 用 Read/Glob/Grep/Task；Claude Code 用对应原生工具。**禁止凭记忆套用某 harness 的专有工具名**（如在 Cursor 误调 Claude Code 专属命令）。

## 任务分类

```
用户输入
  → R18: claude-mem search?（相关则先查）
  → 简单(≤3文件,无架构)? → L1 change-impact → 直接改 → 轻量验证
  → Bug(堆栈/复现)? → L3 triage → L2 debugging
  → 非简单 → L2 brainstorming → …五阶段全链
```

**简单旁路**：不 Read executing-plans / subagent-driven-development。

## P0 路由集（5）

| 等级 | Skill | 触发 |
|------|-------|------|
| L1 | using-superpowers | 会话开始 |
| L1 | change-impact-analysis | 任何修改 |
| L2 | brainstorming | 非简单、方案、架构 |
| L2 | verification-before-completion | 完成、验收 |
| L2 | systematic-debugging | 调试、测试失败 |

## 非简单 L2 链

| 阶段 | Read |
|------|------|
| ② | writing-plans → spec-validation（门控） |
| ③ | executing-plans + subagent-driven-development |
| ④ | verification-before-completion |

## 规格三轨（自动判定，互斥）

| 优先级 | 条件 | 轨道 | L3 追加 |
|--------|------|------|---------|
| 1 | `/workstream` 或「并行流」 | GSD | workstream-management |
| 2 | `openspec/changes/` 或 brownfield | OpenSpec | rules/OPENSPEC.md |
| 3 | ≤3 文件单模块 | 轻量 `spec/` | — |
| 4 | 默认 >3 文件 | OpenSpec | rules/OPENSPEC.md；无目录则创建 change id |

## 调研三档（① brainstorming 内嵌）

| 档 | 场景 | 工具 |
|----|------|------|
| L1 | 单点 API/事实 | Context7 / Exa |
| L2 | 方案对比 | Exa + Firecrawl 单页 |
| L3 | 深度选型、/deep-research | skills/deep-research |

升级：L1 不足→L2→L3。代码库用 codegraph，禁止先用 Firecrawl。

## 调用链

```
MANIFEST.yaml → P0路由集 → 全局 skill → catalog → agent → MCP
```

## 工作流扩展（L3 信号触发）

| 信号 | Skill |
|------|-------|
| 写计划 | writing-plans |
| TDD | test-driven-development |
| 代码审查 | requesting-code-review → eng-reviewer |
| 架构决策 | adr-management |
| 长时自主 | claude-to-deerflow（/deer-flow） |
| Git 提交 | git-workflow |
| 开 PR | pr-workflow |
| 输出冗长 | caveman-compress |

## Token

- Shell：`hook/pre-rtk-rewrite`
- 回复：`skill/caveman-compress`

## 原则

不跳过、不替代、不省略 skill 步骤。
