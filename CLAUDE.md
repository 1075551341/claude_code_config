---
description: Claude 配置总纲 — Tool-First 路由 + 五阶段 + 铁律（多端 L0 必加载）
alwaysApply: true
layer: router
---

# Claude 全局配置

> 五柱×五阶段×三横切 | 归属→`MANIFEST.yaml` | 法典→`SPEC.md` | **v11.4.17**（审查清单闭环：版本映射、L0/MCP 注释、本机落地。原 v11.4.16：MCP 分组。原 v11.4.15：harness 文案。原 v11.4.14：加载器闭环）

**五柱**：Superpowers v6.3.0(方法论，插件随上游自动更新) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem v13.13.1(记忆，钉扎 <13.14)
**三横切**：L1 ECC+deer-flow | L2 RTK+caveman+阈值 | L3 codegraph+外部搜索（harness web_scrape/web_search）— 详见 `rules/CORE.md`

## 总纲链（Tool-First Read，禁止凭记忆执行）

1. **路由入口** — 本文件（编辑器目录 `CLAUDE.md` 软链 → `~/.claude/CLAUDE.md`）
2. **归属矩阵** — `MANIFEST.yaml`（含 harness 清单：hooks 注册/命令/MCP profile，v11 吸收原 agent.yaml）
3. **发现索引** — `skills-INDEX.md` | `agents-INDEX.md` | `rules-INDEX.md`
4. **法典** — `SPEC.md`（变更史 → `CHANGELOG.md`）
5. **按需加载**（任务触发后再 Read，禁止全量扫描）：`skills/<name>/SKILL.md` | `agents/<name>.md` | `rules/<name>.md`（治理详情+最佳实践 → `rules/GOVERNANCE.md`）
6. **场景路由 SSOT** — 分类后 Read `config/scenario-router.yaml` 对应场景（加载列表+质量门）；工具经 `config/harness-capabilities.yaml` 按当前端解析，缺能力走 fallback/interrupt，禁止假装已调用

## 优先级链

```
用户显式指令 > CLAUDE.md > 激活skill > lazy规则 > alwaysApply > 默认
工具路由: codegraph → Grep（codebase-memory 已禁用）| 为什么/偏好 → claude-mem（禁止跳级，见 CORE R17-R18）
```

## P0 路由集（6）= L1×4 + L2 门控×2

| Skill                          | 等级 | 触发                                                      |
| ------------------------------ | ---- | --------------------------------------------------------- |
| using-superpowers              | L1   | 会话开始、分类路由                                        |
| task-triage                    | L1   | 会话开始分类、新任务（判定条件 SSOT，禁止凭本表缩写自判） |
| change-impact-analysis         | L1   | 任何修改意图                                              |
| brainstorming                  | L1   | 非简单 ①规划（grill→HARD-GATE）                           |
| verification-before-completion | L2   | ④验收                                                     |
| systematic-debugging           | L2   | Bug/调试                                                  |

**简单 = Phase0 已盘点 + 关联需改≤2 + 白名单 + 六维全低 + 模型匹配低 + attempt=1（缺一不可）**；持续处理（attempt≥2/首轮未解决）→ 执行升档非简单 + verify_tier=全量。六维矩阵与黑白名单正文只在 `skills/task-triage/SKILL.md`，**禁止在别处复制**。

## 加载等级 L0–L3

| 等级 | 内容                                                                              | 机制                                       |
| ---- | --------------------------------------------------------------------------------- | ------------------------------------------ |
| L0   | 本文件 + rules/CORE.md                                                            | alwaysApply (~6K tokens)                   |
| L1   | using-superpowers, task-triage, change-impact-analysis, brainstorming（会话常驻） | L1 按需全文 Read                           |
| L2   | writing-plans / spec-validation / executing-plans / verification / debugging      | 阶段触发 Read 全文                         |
| L3   | 所有其他 skills/rules/agents/MCP/harness web 工具                                 | description 触发词 + slash 路由，按需 Read |

## 五阶段流程（SSOT）

> 任务入口前置：疑似重复/相关历史 → 先 `claude-mem search`（R18）→ L1 using-superpowers + task-triage（Phase0 盘点）。

```
简单(Phase0盘点+关联需改≤2+白名单+六维全低+模型匹配+attempt=1) → L1 change-impact → 一次改齐 → ④验证(比例)
Bug(多文件/根因不明/执行升档) → triage(L3 P0-P3) → L2 systematic-debugging(根因分析) → ④全量验证
非简单 → ①grill访谈(一次一问+推荐答案，≤5问) → ①规划(Read skills/brainstorming/SKILL.md HARD-GATE)
       → ②规格(Read skills/writing-plans/SKILL.md)
       → ③执行(Read skills/executing-plans/SKILL.md)
       → ④验证(Read skills/verification-before-completion/SKILL.md；全量)
          有代码/配置改动：修改（change-implementer）→验证→审查（eng-reviewer 只找问题）；
          干净 PASS 即停；审查一次找齐后汇总清单再派修改者集中改齐；每轮独立审查必须全新开审（禁止 resume），日常最多 3 轮（单任务覆盖须用户显式声明）；禁止边审边改、禁止审查者改文件、禁止只连审不改；满轮未过 → BLOCKED/DONE_WITH_CONCERNS
          计划未批准 / CreatePlan 等待用户 → 禁止声称完成与审查
          → ⑤学习
非简单 调研 → deep-research（L3 双源）
```

> 分类 SSOT → `skills/task-triage/SKILL.md`。任意大类完成前均须验证；初判简单但持续处理（attempt≥2/首轮未解决）→ **执行升档非简单** + verify_tier=全量。简单旁路不 Read executing-plans/subagent-driven-development。

<HARD-GATE>用户批准设计前禁止实现 → Read skills/brainstorming/SKILL.md</HARD-GATE>

**状态机**：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
**显式触发（v10.15）**：TDD(RED→GREEN→REFACTOR) 与 SDD(subagent-driven-development 子Agent派发) **仅用户明确要求时启用**；默认非简单走 ①-⑤ 骨架由主会话直接执行，不强制写测试先行、不强制子Agent派发。

```
门控（失败转移）:
  ① 规划: HARD-GATE 用户批准设计 ✓（未批准 → 回到①）
  ② 规格: spec-validation通过 + 任务有成功标准 + 无静默缩scope（失败 → BLOCKED，禁止 execute）
  ③ 执行: 子任务完成 + 构建/类型/Lint通过 + 子Agent异常已处理(R16)（失败 → BLOCKED + R16 报告）
  ④ 验证: 质量门全通过 + 交叉验证通过 + 会话终验(R20)按原始要求逐条回放（满足/遗漏/错改/漏改/原功能/影响范围；配置/修改必须与文档/注释同步；未全绿 → DONE_WITH_CONCERNS 需说明）。有代码/配置改动：change-implementer 修改→验证→eng-reviewer 一次找齐；干净 PASS 即停；清单齐后集中改；每轮全新开审（日常最多 3 轮，单任务覆盖须用户显式声明）；只读免审；计划未批准禁止声称完成。Claude Stop exit 2；Cursor 无完成门 followup
  ⑤ 学习: 模式提取完成（claude-mem pattern）
```

## 铁律 R1–R20

| #   | 约束        | 核心                                                                                                                                                | 全文    |
| --- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| R1  | 任务完成    | 验证通过才算完成                                                                                                                                    | —       |
| R2  | 修改确认    | Read→Edit→Read                                                                                                                                      | —       |
| R3  | Bug修复     | Grep全修→确认                                                                                                                                       | —       |
| R4  | 配置变更    | Grep引用→构建                                                                                                                                       | —       |
| R5  | 重试上限    | 同方案≤2次                                                                                                                                          | —       |
| R6  | 非简单      | ①→⑤全流程                                                                                                                                           | —       |
| R7  | 交叉验证    | 完成前验证清单                                                                                                                                      | —       |
| R8  | 高危确认    | 删数据/强推main前确认                                                                                                                               | —       |
| R9  | 命令安全    | Windows终端优先pwsh(PS7+稳定版)；禁cd+重定向/powershell -Command；Qoder MCP启动脚本例外                                                             | —       |
| R10 | 简洁优先    | 高内聚低耦合易迭代                                                                                                                                  | —       |
| R11 | 安全默认    | 不信任输入、无硬编码密钥                                                                                                                            | —       |
| R12 | 子Agent隔离 | fresh context+制品通信                                                                                                                              | CORE.md |
| R13 | 制品存活    | 跨会话持久化                                                                                                                                        | CORE.md |
| R14 | 版本克制    | 非必要不升major                                                                                                                                     | CORE.md |
| R15 | 包管理器    | pnpm优先；npm兜底                                                                                                                                   | CORE.md |
| R16 | 错误暴漏    | 禁止裸except:pass                                                                                                                                   | CORE.md |
| R17 | 代码探索    | codegraph 首选；cbm 已禁用；禁跳级                                                                                                                  | CORE.md |
| R18 | 记忆优先    | 为什么/约定/偏好→claude-mem                                                                                                                         | CORE.md |
| R19 | Git 禁令    | 禁自动stash/commit                                                                                                                                  | CORE.md |
| R20 | 会话终验    | 改前优先成熟方案；完成后逐条回放满足/遗漏/错改/漏改/原功能/影响范围；核对范围=影响面全部相关项；**配置/修改必须与文档/注释同步**；独立审查一次找齐且**每轮全新开审**，修改必须 `change-implementer` 按完整清单集中改；禁止边审边改耗轮次；**验证证据须观察输出**。模板→verification skill | CORE.md |

> 工程原则（第一性原理/YAGNI/依赖克制/删除过时优先）→ `rules/CORE.md` 工程原则节 + `rules/GOVERNANCE.md` 最佳实践详参章

## Tool-First 路由与场景-工具映射

```
task-triage → config/scenario-router.yaml → Read load.* → config/harness-capabilities.yaml 解析 capability
```

场景→技能/工具/质量门 **只在** `config/scenario-router.yaml`；端能力 **只在** `config/harness-capabilities.yaml`。矩阵正文禁止在本文件复制。原则：内置>plugin>MCP>中断启用；codegraph=怎么运作；CRG=影响面/审查；claude-mem=为什么/偏好。

**阈值**：见 CORE.md 三级阈值 | GSD **70%逻辑断点**（任务边界） | ⛔100% | **压缩**：Cursor→`/summarize`；Claude Code→`/compact`（auto-compact 配置 → `rules/CONTEXT.md`）
**调研三档**（L1→L2→L3决策标准） → `skills/deep-research/SKILL.md` | **规格三轨**（OpenSpec/GSD/轻量，互斥） → `rules/OPENSPEC.md`

## 工具调用门控

**禁止场景**（违反即阻断）：

- eligible git 仓无双图时 Grep/Glob/编辑/查询 MCP → 图谱保鲜硬门 deny（须先 `codegraph init -i` / `code-review-graph build`）
- 未调用 `codegraph_explore` 直接 Grep/Read 代码结构 → 违反R17
- 未调用 `claude-mem search` 直接重复 Read 相同文件 → 违反R18
- 未按当前 harness 的 `web_scrape`+`web_search`（Firecrawl+Exa，或 Cursor 等端的 fallback）做 L3 双源，只用 WebFetch/WebSearch 并假装已交叉 → 违反L3
- 上下文>70% 未评估压缩（RTK/caveman） → 违反阈值铁律

**强制场景**（HARD-GATE）：

- 任务分类：必须 Read `skills/task-triage/SKILL.md`（Phase0 盘点；持续处理→执行升档非简单；非简单先 grill；完成前均须验证）
- ①规划阶段：必须 Read `skills/brainstorming/SKILL.md`（用户批准设计前禁止实现）
- ④验证阶段：必须 Read `skills/verification-before-completion/SKILL.md`
- Bug修复：必须 Read `skills/systematic-debugging/SKILL.md`

## 审查路由

```
独立审前：双图 ensure（codegraph init|sync + code-review-graph build|update）
所有变更→eng-reviewer（只找问题）| 产品→+ceo | UI/UX→+designer+dx-reviewer
有代码/配置改动：change-implementer 修改→验证→审查一次找齐后汇总；干净 PASS 即停；清单齐后再派修改者集中改齐；每轮全新开审（禁止 resume）；日常最多 3 轮（单任务覆盖须用户显式声明）
并行审查：仅当只读 + 维度不重叠 + 子代理 model=inherit（禁止 max/xhigh/thinking-max 倍率档）；否则串行
禁止边审边改、禁止审查者改文件、禁止只连审不改。计划未批准禁止声称完成。Cursor 完成门不 followup
安全→+security-reviewer(深度模式) | 跨模型→+codex-reviewer | catalog/agents/ 按需
```

## 命令速查

| 命令                                  | 阶段     | 作用                       |
| ------------------------------------- | -------- | -------------------------- |
| /discuss /plan /execute /verify /ship | ①-⑤      | 五阶段                     |
| /deep-research                        | ①调研 L3 | harness `web_scrape`+`web_search`（Firecrawl+Exa 或当前端 fallback）+交叉验证 |
| /workstream                           | GSD      | 并行任务流                 |
| /adr                                  | ①        | 架构决策                   |
| /opsx:sync                            | ②        | OpenSpec delta 同步主 spec |

> 命令全集 → `commands/`（18 个，命令为薄壳，正文在对应 skill）；deer-flow 编排经 `catalog/skills/claude-to-deerflow` 按需复制启用。
> **OpenSpec OPSX**：`/opsx:propose` → `continue|ff` → `apply` → `verify` → `sync` → `archive` | CLI: `openspec init --tools cursor`（profile: core）

## 指针

| 内容             | 位置                                                                                     |
| ---------------- | ---------------------------------------------------------------------------------------- |
| 归属矩阵/harness | MANIFEST.yaml                                                                            |
| 法典/架构        | SPEC.md + CHANGELOG.md                                                                   |
| 铁律/编码/阈值   | rules/CORE.md                                                                            |
| 工作流/DAG       | rules/WORKFLOW.md                                                                        |
| Agent 协作       | rules/AGENTS.md                                                                          |
| 场景路由/端能力  | config/scenario-router.yaml + config/harness-capabilities.yaml                           |
| MCP 规范 SSOT    | rules/MCP.md（矩阵指针→场景 YAML；Cursor 差异→docs/CURSOR_MCP_PROFILE.md）               |
| 调研 SSOT        | docs/research/44-repo-deep-research-v10.11.md + repos/                                   |
| 同步指南         | docs/SYNC_GUIDE.md                                                                       |
| Git/PR 流程      | skills/git-workflow, skills/pr-workflow                                                  |
| 记忆搜索         | claude-mem (R18)                                                                         |

**插件**：见 `plugins/installed_plugins.json` + `settings.json` enabledPlugins（Cursor 禁用 compound-engineering，与本地 agents 重叠）。
**同步**：`scripts/sync.ps1` — v11.1 多编辑器 1+N：Claude Code 原生读 `~/.claude`（零同步）；Cursor 软链 L0 入口（6 根文件）+ local plugin 实体规则（唯一规则通道，`~/.cursor/rules` 不生效）；qoder-cn rules（.mdc 实体+台账）、trae-cn user_rules（.md 实体+台账）、workbuddy 仅 CLAUDE.md+skills 联接；qoder/trae/codearts 定义保留待装；DSH/OpenCode 仅复制便携件，**禁止 CLAUDE.md 覆盖 AGENTS.md**；清单/常量单源 `config/sync-manifest.json`（home 缺席自动跳过）。
**业务仓库**：SessionStart 对 eligible git 仓 **执行** `codegraph init|sync` 与 `code-review-graph build|update`（无图禁止后续探索/编辑，不是仅提示）；有图后改前/完成前走 CRG 上下文与影响面；探索「怎么运作」一律 codegraph_explore（R17）；验证全绿后才跑 `scripts/sync.ps1`。codebase-memory 已永久禁用。
**Karpathy 四原则** → `skills/karpathy-guidelines/SKILL.md`（L3 按需）。**RTK**（shell 输出压缩）由 `pre-rtk-rewrite.py` hook 自动执行 → 详见 `RTK.md`。
