---
description: Claude 配置总纲 — Tool-First 路由 + 五阶段 + 铁律（多端 L0 必加载）
alwaysApply: true
layer: router
---

# Claude 全局配置

> 五柱×五阶段×三横切 | 归属→`MANIFEST.yaml` | 法典→`SPEC.md` | **v11.6.0**（工具链 SSOT：pwsh 7.5+ / pnpm 11。史→`CHANGELOG.md`）

**五柱**：Superpowers v6.3.0(方法论，插件随上游自动更新) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem v13.13.1(记忆，钉扎 <13.14)
**三横切**：L1 ECC+deer-flow | L2 RTK+caveman+阈值 | L3 codegraph+Firecrawl/Exa（codebase-memory 已禁用）— 详见 `rules/CORE.md`

## 总纲链（Tool-First Read，禁止凭记忆执行）

1. **路由入口** — 本文件（编辑器目录 `CLAUDE.md` 软链 → `~/.claude/CLAUDE.md`）
2. **归属矩阵** — `MANIFEST.yaml`（含 harness 清单：hooks 注册/命令/MCP profile）
3. **发现索引** — `skills-INDEX.md` | `agents-INDEX.md` | `rules-INDEX.md`
4. **法典** — `SPEC.md`（变更史 → `CHANGELOG.md`）
5. **按需加载**：`skills/<name>/SKILL.md` | `agents/<name>.md` | `rules/<name>.md`（治理详参 → `rules/GOVERNANCE.md`）

## 优先级链

```
用户显式指令 > CLAUDE.md > 激活skill > lazy规则 > alwaysApply > 默认
工具路由: codegraph →（双图就绪后）Grep；本机文件名 → everything（禁止替代 Glob/R17）| 为什么/偏好 → claude-mem（CORE R17-R18）
```

## P0 路由集（6）= L1×4 + L2 门控×2

| Skill | 等级 | 触发 |
| ------------------------------ | ---- | --------------------------------------------------------- |
| using-superpowers | L1 | 会话开始、分类路由 |
| task-triage | L1 | 会话开始分类、新任务（判定条件 SSOT，禁止凭本表缩写自判） |
| change-impact-analysis | L1 | 任何修改意图 |
| brainstorming | L1 | 非简单 ①规划（grill→HARD-GATE） |
| verification-before-completion | L2 | ④验收（审查政策 + R20 七维 SSOT） |
| systematic-debugging | L2 | Bug/调试 |

**简单 = Phase0 已盘点 + 关联需改≤2 + 白名单 + 六维全低 + 模型匹配低 + attempt=1（缺一不可）**；持续处理（attempt≥2/首轮未解决）→ 执行升档非简单 + verify_tier=全量。六维与黑白名单只在 `skills/task-triage/SKILL.md`。

## 加载等级 L0–L3

| 等级 | 内容 | 机制 |
| ---- | --------------------------------------------------------------------------------- | ------------------------------------------ |
| L0 | 本文件 + rules/CORE.md | alwaysApply |
| L1 | using-superpowers, task-triage, change-impact-analysis, brainstorming | L1 按需全文 Read |
| L2 | writing-plans / spec-validation / executing-plans / verification / debugging | 阶段触发 Read 全文 |
| L3 | 其他 skills/rules/agents/MCP/Firecrawl/Exa | description + slash，按需 Read |

## 五阶段流程（SSOT）

> 入口：疑似重复/相关历史 → `claude-mem search`（R18）→ using-superpowers + task-triage（Phase0）。

```
简单 → change-impact → 一次改齐 → ④验证 → 审查前刷图 → 全新只读独立审查 → 短 R20
Bug(多文件/根因不明/执行升档) → triage → systematic-debugging → ④全量（同上审查）
非简单 → ①grill(≤5) → ①规划(brainstorming HARD-GATE) → ②规格(writing-plans)
       → ③执行(executing-plans) → ④验证(verification-before-completion)
       → ⑤学习
非简单调研 → deep-research（L3 双源）
```

> 分类 → `skills/task-triage/SKILL.md`。任意大类完成前均须验证。**审查/R20/轮次/图谱** 正文只在 verification skill + `config/quality_gates.json`（`review_max_rounds`；`max_blocks` 仍为 Stop 验证阻断）。计划未批准 / 仅 `*.plan.md` / 纯澄清问答（无交付）不进入完成态。简单旁路不 Read executing-plans/subagent-driven-development。

<HARD-GATE>用户批准设计前禁止实现 → Read skills/brainstorming/SKILL.md</HARD-GATE>

**状态机**：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
**显式触发**：TDD 与 SDD **仅用户明确要求时启用**。

```
门控: ① HARD-GATE 批准设计  ② spec-validation + 成功标准  ③ 构建/Lint + R16
④ 质量门 + 交叉验证 + R20 七维（满足/遗漏/错改/漏改/原功能/影响范围/问题是否解决；配置/修改必须与文档/注释同步）
   改→验→审查前刷图→并行全新审查。政策 → verification skill。Claude Stop exit 2；Cursor 无完成门 followup
⑤ claude-mem pattern
```

## 铁律 R1–R20

| # | 约束 | 核心 | 全文 |
| --- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| R1 | 任务完成 | 验证通过才算完成 | — |
| R2 | 修改确认 | Read→Edit→Read | — |
| R3 | Bug修复 | Grep全修→确认 | — |
| R4 | 配置变更 | Grep引用→构建 | — |
| R5 | 重试上限 | 同方案≤2次 | — |
| R6 | 非简单 | ①→⑤全流程 | — |
| R7 | 交叉验证 | 完成前验证清单 | — |
| R8 | 高危确认 | 删数据/强推main前确认 | — |
| R9 | 命令安全 | Windows 一律 pwsh 7.5+；禁 cd+重定向/`powershell -Command`；MCP spawn → `rules/MCP.md` | — |
| R10 | 简洁优先 | 高内聚低耦合易迭代 | — |
| R11 | 安全默认 | 不信任输入、无硬编码密钥 | — |
| R12 | 子Agent隔离 | fresh context+制品通信 | CORE.md |
| R13 | 制品存活 | 跨会话持久化 | CORE.md |
| R14 | 版本克制 | 非必要不升major | CORE.md |
| R15 | 包管理器 | pnpm 11；缺则 BLOCKED | CORE.md |
| R16 | 错误暴漏 | 禁止裸except:pass | CORE.md |
| R17 | 代码探索 | codegraph 首选；cbm 已禁用；禁跳级 | CORE.md |
| R18 | 记忆优先 | 为什么/约定/偏好→claude-mem | CORE.md |
| R19 | Git 禁令 | 禁自动stash/commit | CORE.md |
| R20 | 会话终验 | 七维回放 + 文档/注释同步 + 审查前刷图 + 每轮全新开审；修改走 `change-implementer`；证据须观察输出。模板→verification skill | CORE.md |

> 工程原则 → `rules/CORE.md` + `rules/GOVERNANCE.md`

## Tool-First 路由与场景-工具映射

```
MANIFEST → P0路由集(6) → 全局 skill → catalog → agent → MCP
```

| 场景 | 首选工具 | 禁止替代 | 触发条件 |
| ---------------------- | ------------------- | ------------------- | ------------------------- |
| 结构/调用链/怎么运作 | `codegraph_explore` | Grep/Read/Glob/everything；调用 cbm | 任何代码结构理解 |
| 精准上下文/变更影响/风险/审查/PR | CRG `get_minimal_context` / `get_impact_radius` / `detect_changes` / `get_review_context` | 用 codegraph 做 test-gap；无图仍假装已审 | 有 `.code-review-graph/` 的改前/完成前/开 PR |
| 本机按文件名（跨仓/全盘） | `everything_search` | 工作区 Glob；R17 探索 | Windows + Everything 运行中 |
| 为什么/约定/偏好 | `claude-mem search` | 塞入 codegraph | 代码推不出的信息 |
| 网页深度调研 | `Firecrawl+Exa` | WebFetch | /deep-research 或调研意图 |
| Shell输出压缩 | RTK (hook自动) | 原生Bash | 任何Bash调用 |
| 输出压缩 | caveman | 原生输出 | 上下文>70% |

**阈值**：CORE.md | GSD **70%逻辑断点** | ⛔100% | 压缩：Cursor→`/summarize`；Claude Code→`/compact`（`rules/CONTEXT.md`）
**调研三档** → `skills/deep-research/SKILL.md` | **规格三轨** → `rules/OPENSPEC.md`

## 工具调用门控

**禁止**：eligible git 仓无双图时 Grep/Glob/everything/编辑/查询 MCP；未 `codegraph_explore` 直接 Grep/Read/Glob/everything 结构探索；未 `claude-mem search` 重复 Read 同文件；未 Firecrawl+Exa 做深度调研；上下文>70% 未评估压缩。

**强制**：分类 Read `skills/task-triage/SKILL.md`；①规划 Read `skills/brainstorming/SKILL.md`；④验证 Read `skills/verification-before-completion/SKILL.md`；Bug Read `skills/systematic-debugging/SKILL.md`。

## 审查路由

> 正文 → `rules/AGENTS.md`；政策/七维/轮次 → verification skill。必派 `eng-reviewer`；产品 `+ceo-reviewer`；UI `+designer`+`dx-reviewer`；安全 `+security-reviewer`；测试边界 `+qa`。无依赖同一消息并行 Task；有依赖串行。审查者只读；修改只走 `change-implementer`。

## 命令速查

| 命令 | 阶段 | 作用 |
| ------------------------------------- | -------- | -------------------------- |
| /discuss /plan /execute /verify /ship | ①-⑤ | 五阶段 |
| /deep-research | ①调研 L3 | Firecrawl+Exa+交叉验证 |
| /workstream | GSD | 并行任务流 |
| /adr | ① | 架构决策 |
| /opsx:sync | ② | OpenSpec delta 同步主 spec |

> 命令全集 → `commands/`。OPSX：`/opsx:propose` → `continue|ff` → `apply` → `verify` → `sync` → `archive`。

## 指针

| 内容 | 位置 |
| ---------------- | ---------------------------------------------------------------------------------------- |
| 归属/harness | MANIFEST.yaml |
| 法典/变更史 | SPEC.md + CHANGELOG.md |
| 铁律/编码/图谱 | rules/CORE.md |
| 工具链地板 | config/toolchain.yaml |
| 工作流/Agent/MCP | rules/WORKFLOW.md / AGENTS.md / MCP.md |
| 同步 | docs/SYNC_GUIDE.md |
| 记忆 | claude-mem (R18) |

**插件**：`plugins/installed_plugins.json` + `settings.json` enabledPlugins。
**同步**：`scripts/sync.ps1` — Claude Code 零同步；Cursor/Qoder/TRAE/Codearts 见 SYNC_GUIDE。不碰 `settings.json` / `.mcp.json` / `hooks/`。
**业务仓库**：任务开始 SessionStart **ensure** 双图；每轮开审前须 **last_edit 之后** 增量 refresh；完成后 Stop refresh。无图 deny。探索走 `codegraph_explore`。验绿后 `scripts/sync.ps1`。
**Karpathy 四原则** → `skills/karpathy-guidelines/SKILL.md`。**RTK** → `RTK.md`。
