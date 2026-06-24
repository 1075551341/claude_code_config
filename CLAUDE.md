---
description: 
alwaysApply: true
---

# Claude 全局配置

> 五柱×五阶段×三横切 | 路由→`CLAUDE-ROUTER.mdc` | 归属→`MANIFEST.yaml` | 法典→`SPEC.md` | **v10.3**

**五柱**：Superpowers v6.0.0(方法论) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem(记忆)
**三横切**：L1 ECC+deer-flow | L2 RTK+caveman+阈值 | L3 codegraph+Firecrawl/Exa — 详见 `rules/CORE.md`

---

## 优先级链

```
用户显式指令 > CLAUDE.md > 激活skill > lazy规则 > alwaysApply > 默认
工具路由: codegraph_explore > Grep | claude-mem search > 重复Read
```

---

## 五阶段流程（SSOT）

```
简单(≤3文件) → L1 change-impact → 执行 → 轻量验证
Bug → triage(L2 P0-P3) → L2 systematic-debugging(根因分析)
非简单 → ①规划(Read skills/brainstorming/SKILL.md HARD-GATE)
       → ②规格(Read skills/writing-plans/SKILL.md)
       → ③执行(Read skills/executing-plans/SKILL.md)
       → ④验证(Read skills/verification-before-completion/SKILL.md)
       → ⑤学习
```

<HARD-GATE>用户批准设计前禁止实现 → Read skills/brainstorming/SKILL.md</HARD-GATE>

**状态机**：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
**SDD+TDD**：spec→writing-plans(原子)→subagent(两阶段审查)→verify | RED→GREEN→REFACTOR

```
门控:
  ① 规划: HARD-GATE 用户批准设计 ✓
  ② 规格: spec-validation通过 + 任务有成功标准 + 无静默缩scope
  ③ 执行: 子任务完成 + 构建/类型/Lint通过 + 子Agent异常已处理(R16)
  ④ 验证: 质量门全通过 + 交叉验证通过
  ⑤ 学习: 模式提取完成
```

---

## 铁律 R1–R19

| # | 约束 | 核心 | 全文 |
|---|------|------|------|
| R1 | 任务完成 | 验证通过才算完成 | — |
| R2 | 修改确认 | Read→Edit→Read | — |
| R3 | Bug修复 | Grep全修→确认 | — |
| R4 | 配置变更 | Grep引用→构建 | — |
| R5 | 重试上限 | 同方案≤2次 | — |
| R6 | 非简单 | ①→⑤全流程 | — |
| R7 | 交叉验证 | 完成前验证清单 | — |
| R8 | 高危确认 | 删数据/强推main前确认 | — |
| R9 | 命令安全 | 禁cd+重定向/powershell -Command | — |
| R10 | 简洁优先 | 高内聚低耦合 | — |
| R11 | 安全默认 | 不信任输入、无硬编码密钥 | — |
| R12 | 子Agent隔离 | fresh context+制品通信 | CORE.md |
| R13 | 制品存活 | 跨会话持久化 | CORE.md |
| R14 | 版本克制 | 非必要不升major | CORE.md |
| R15 | 包管理器 | pnpm优先；npm兜底 | CORE.md |
| R16 | 错误暴漏 | 禁止裸except:pass | CORE.md |
| R17 | 代码探索 | codegraph_explore首选→Grep | CORE.md |
| R18 | 记忆优先 | claude-mem先于重复分析 | CORE.md |
| R19 | Git 禁令 | 禁自动stash/commit | CORE.md |

---

## Tool-First 路由

```
MANIFEST → P0路由集(5) → 全局 skill → catalog → agent → MCP
```

> **代码探索铁律（R17）**：结构/调用链/影响面 **必先 `codegraph_explore`**（默认工具，blast-radius 含影响面），次选 Grep 精确定位，禁止未探索就大范围 Read。`codegraph_impact` 默认不暴露（F1），需 `CODEGRAPH_MCP_TOOLS` env 或 CLI。codegraph 返回的源码视为已读，不重复 Read/Grep。

**五轨**：codegraph(R17) | Firecrawl+Exa | claude-mem(R18) | Context7
**Token**：RTK(shell) + caveman(输出) + codegraph(探索)
**阈值**：见 CORE.md 三级阈值 | GSD **70%逻辑断点**（任务边界） | ⛔100%
**压缩**：Cursor→`/summarize`；Claude Code→`/compact`

**P0路由集** → `CLAUDE-ROUTER.mdc` | **加载等级 L0–L3** → `CLAUDE-ROUTER.mdc`
**调研三档**（L1→L2→L3决策标准） → `skills/deep-research/SKILL.md`
**规格三轨**（OpenSpec/GSD/轻量，互斥） → `rules/OPENSPEC.md`

---

## 审查路由

```
所有变更→eng-reviewer | 产品→+ceo | UI/UX→+designer+dx-reviewer
安全→+security-reviewer | iOS→+ios-specialist | 跨模型→+codex-reviewer
```

---

## 命令速查

| 命令 | 阶段 | 作用 |
|------|------|------|
| /discuss /plan /execute /verify /ship | ①-⑤ | 五阶段 |
| /deep-research | ①调研 L3 | Firecrawl+Exa+交叉验证 |
| /deer-flow | ③执行 L3 | 外部编排（>30min 自主任务） |
| /workstream | GSD | 并行任务流 |
| /adr | ① | 架构决策 |
| /opsx:sync | ② | OpenSpec delta 同步主 spec |

**OpenSpec OPSX**：`/opsx:propose` → `continue|ff` → `apply` → `verify` → `sync` → `archive` | CLI: `openspec init --tools cursor`（profile: core）

---

## 指针

| 内容 | 位置 |
|------|------|
| 路由入口/加载等级 | CLAUDE-ROUTER.mdc |
| 归属矩阵 | MANIFEST.yaml |
| 法典/架构 | SPEC.md (v10.3) |
| 铁律/编码/阈值 | rules/CORE.md |
| 工作流/DAG | rules/WORKFLOW.md |
| Agent 协作 | rules/AGENTS.md |
| 调研 SSOT | docs/research/30-repo-deep-research-v10.md + repos/ |
| 同步指南 | docs/SYNC_GUIDE.md |
| MCP 规范 | docs/TOOL_MATCHING_GUIDE.md, docs/CURSOR_MCP_PROFILE.md |
| Git/PR 流程 | skills/git-workflow, skills/pr-workflow |
| 记忆搜索 | claude-mem (R18) |

**插件**：~/.claude 15启用；Cursor 禁用 compound-engineering（与本地 agents 重叠）。
**同步**：`scripts/sync.ps1` 软链 L0 入口；skills/agents/rules 按需 Read，不复制。
**业务仓库**：进入时检测 `.codegraph/` → 无则提示 `codegraph init`（R17 降本增效）。
**Karpathy 四原则** → `skills/karpathy-guidelines/SKILL.md`（L3 按需）。

@RTK.md
