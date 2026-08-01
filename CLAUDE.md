---
description:
alwaysApply: true
---

# Claude 全局配置

> 五柱×五阶段×三横切 | 路由→`CLAUDE-ROUTER.mdc` | 归属→`MANIFEST.yaml` | 法典→`SPEC.md` | **v10.13.0**

**五柱**：Superpowers v6.2.0(方法论，插件随上游自动更新) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem v13.12.4(记忆)
**三横切**：L1 ECC+deer-flow | L2 RTK+caveman+阈值 | L3 codegraph+Firecrawl/Exa（codebase-memory 已禁用：全盘索引爆 CPU/内存）— 详见 `rules/CORE.md`

---

## 优先级链

```
用户显式指令 > CLAUDE.md > 激活skill > lazy规则 > alwaysApply > 默认
工具路由: codegraph → Grep（codebase-memory 已禁用）| 为什么/偏好 → claude-mem（禁止跳级，见 CORE R17-R18）
```

---

## 五阶段流程（SSOT）

```
简单(Phase0盘点+关联需改≤2+白名单+六维全低+模型匹配+attempt=1) → L1 change-impact → 一次改齐 → ④验证(比例)
Bug(多文件/根因不明/执行升档) → triage(L3 P0-P3) → L2 systematic-debugging(根因分析) → ④全量验证
非简单 → ①grill访谈(一次一问+推荐答案) → ①规划(Read skills/brainstorming/SKILL.md HARD-GATE)
       → ②规格(Read skills/writing-plans/SKILL.md)
       → ③执行(Read skills/executing-plans/SKILL.md)
       → ④验证(Read skills/verification-before-completion/SKILL.md；全量)
       → ⑤学习
```

> 分类 SSOT → `skills/task-triage/SKILL.md`。任意大类完成前均须验证；初判简单但持续处理（attempt≥2/首轮未解决）→ **执行升档非简单** + verify_tier=全量。

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

| #   | 约束        | 核心                               | 全文    |
| --- | ----------- | ---------------------------------- | ------- |
| R1  | 任务完成    | 验证通过才算完成                   | —       |
| R2  | 修改确认    | Read→Edit→Read                     | —       |
| R3  | Bug修复     | Grep全修→确认                      | —       |
| R4  | 配置变更    | Grep引用→构建                      | —       |
| R5  | 重试上限    | 同方案≤2次                         | —       |
| R6  | 非简单      | ①→⑤全流程                          | —       |
| R7  | 交叉验证    | 完成前验证清单                     | —       |
| R8  | 高危确认    | 删数据/强推main前确认              | —       |
| R9  | 命令安全    | 禁cd+重定向/powershell -Command    | —       |
| R10 | 简洁优先    | 高内聚低耦合易迭代                 | —       |
| R11 | 安全默认    | 不信任输入、无硬编码密钥           | —       |
| R12 | 子Agent隔离 | fresh context+制品通信             | CORE.md |
| R13 | 制品存活    | 跨会话持久化                       | CORE.md |
| R14 | 版本克制    | 非必要不升major                    | CORE.md |
| R15 | 包管理器    | pnpm优先；npm兜底                  | CORE.md |
| R16 | 错误暴漏    | 禁止裸except:pass                  | CORE.md |
| R17 | 代码探索    | codegraph 首选；cbm 已禁用；禁跳级 | CORE.md |
| R18 | 记忆优先    | 为什么/约定/偏好→claude-mem        | CORE.md |
| R19 | Git 禁令    | 禁自动stash/commit                 | CORE.md |

---

## Tool-First 路由

```
MANIFEST → P0路由集(6) → 全局 skill → catalog → agent → MCP
```

> **代码探索（R17 铁律）** → SSOT `rules/CORE.md`：codegraph_explore 首选（禁止直接 Grep/Read）；codebase-memory 已禁用（全盘索引爆 CPU/内存）；为什么/偏好 → claude-mem。

**五轨**：codegraph(R17) | Firecrawl+Exa | claude-mem(R18) | Context7
**Token**：RTK(shell) + caveman(输出) + codegraph(探索)
**阈值**：见 CORE.md 三级阈值 | GSD **70%逻辑断点**（任务边界） | ⛔100%
**压缩**：Cursor→`/summarize`；Claude Code→`/compact`

**P0路由集** → `CLAUDE-ROUTER.mdc` | **加载等级 L0–L3** → `CLAUDE-ROUTER.mdc`
**调研三档**（L1→L2→L3决策标准） → `skills/deep-research/SKILL.md`
**规格三轨**（OpenSpec/GSD/轻量，互斥） → `rules/OPENSPEC.md`

---

## 工具调用门控（v10.5.2新增）

**禁止场景**（违反即阻断）：

- 未调用 `codegraph_explore` 直接 Grep/Read 代码结构 → 违反R17
- 未调用 `claude-mem search` 直接重复 Read 相同文件 → 违反R18
- 未调用 `Firecrawl+Exa` 直接使用 WebFetch/WebSearch 深度调研 → 违反L3双源
- 上下文>70% 未评估压缩（RTK/caveman） → 违反阈值铁律

**强制场景**（HARD-GATE）：

- 任务分类：必须 Read `skills/task-triage/SKILL.md`（Phase0 盘点；简单=关联需改≤2+白名单+六维全低+模型匹配+attempt=1；持续处理→执行升档非简单；非简单先 grill；完成前均须验证）
- ①规划阶段：必须 Read `skills/brainstorming/SKILL.md`（用户批准设计前禁止实现）
- ④验证阶段：必须 Read `skills/verification-before-completion/SKILL.md`
- Bug修复：必须 Read `skills/systematic-debugging/SKILL.md`

---

## 审查路由

```
所有变更→eng-reviewer | 产品→+ceo | UI/UX→+designer+dx-reviewer
安全→+security-reviewer | iOS→+ios-specialist | 跨模型→+codex-reviewer
```

---

## 命令速查

| 命令                                  | 阶段     | 作用                       |
| ------------------------------------- | -------- | -------------------------- |
| /discuss /plan /execute /verify /ship | ①-⑤      | 五阶段                     |
| /deep-research                        | ①调研 L3 | Firecrawl+Exa+交叉验证     |
| /workstream                           | GSD      | 并行任务流                 |
| /adr                                  | ①        | 架构决策                   |
| /opsx:sync                            | ②        | OpenSpec delta 同步主 spec |

> 命令全集 → `commands/`（18 个）；deer-flow 外部编排经 `skills/claude-to-deerflow` 触发（无独立命令）。

**OpenSpec OPSX**：`/opsx:propose` → `continue|ff` → `apply` → `verify` → `sync` → `archive` | CLI: `openspec init --tools cursor`（profile: core）

---

## 指针

| 内容              | 位置                                                    |
| ----------------- | ------------------------------------------------------- |
| 路由入口/加载等级 | CLAUDE-ROUTER.mdc                                       |
| 归属矩阵          | MANIFEST.yaml                                           |
| 法典/架构         | SPEC.md (v10.13.0)                                      |
| 铁律/编码/阈值    | rules/CORE.md                                           |
| 工作流/DAG        | rules/WORKFLOW.md                                       |
| Agent 协作        | rules/AGENTS.md                                         |
| 调研 SSOT         | docs/research/44-repo-deep-research-v10.11.md + repos/  |
| 同步指南          | docs/SYNC_GUIDE.md                                      |
| MCP 规范          | docs/TOOL_MATCHING_GUIDE.md, docs/CURSOR_MCP_PROFILE.md |
| Git/PR 流程       | skills/git-workflow, skills/pr-workflow                 |
| 记忆搜索          | claude-mem (R18)                                        |

**插件**：见 `plugins/installed_plugins.json` + `settings.json` enabledPlugins（Cursor 禁用 compound-engineering，与本地 agents 重叠）。
**同步**：`scripts/sync.ps1`（v18.2）— 软链 L0 入口 + Cursor local plugin 实体规则（唯一规则通道）；skills/agents/rules 按需 Read，不复制。
**业务仓库**：进入时检测 `.codegraph/` → 无则提示 `codegraph init`；探索一律 codegraph_explore（R17），索引缺失→`scripts/cbm-index.ps1` 已弃用，改 `codegraph init`；codebase-memory 已禁用。
**Karpathy 四原则** → `skills/karpathy-guidelines/SKILL.md`（L3 按需）。

**RTK**（shell 输出压缩）由 `pre-rtk-rewrite.py` hook 自动执行 → 详见 `RTK.md`（按需 Read，不常驻全文）。
