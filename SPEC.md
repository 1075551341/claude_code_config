# SPEC.md — 配置法典索引

> CLAUDE.md 为路由层（≤200行）；本文件为法典索引；变更史 → `CHANGELOG.md`。
> 版本：11.4.13 | 五柱×五阶段×三横切 | L0–L3 分级加载 + 场景路由 YAML SSOT + harness 能力图 + MCP 常驻 4 项（codegraph/CRG/serena/grep）+ 独立审前双图 ensure + inherit 并行审查（禁倍率档）+ 图谱保鲜硬门 + Cursor 完成门不再 followup + 审查一次找齐再集中改 + 每轮全新开审 + 审查只找问题、修改走 change-implementer + 配置/文档/注释必须同步 + 短 R20 + 有改动即双审 + TDD/SDD 显式触发 + 多编辑器 1+N + DSH/OpenCode 适配层 | UA removed | cbm 已禁用

---

## 架构公式

```
RUNTIME  = Superpowers(方法论) + GSD Redux(上下文) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
FORMAT   = ECC模式(cherry-pick) + anthropics/skills(格式) + best-practice(实证)
REVIEW   = gstack 6审查 + 3补全 + 1跨模型
OPTIMIZE = RTK(shell token) + caveman(输出token)
INSIGHT  = codegraph(R17 常驻) + codebase-memory(已禁用：全盘索引爆 CPU/内存，codegraph 全权替代) + Exa/Firecrawl(外部调研)  # UA removed v10.5
EXTERNAL = deer-flow 2.0(LangGraph编排,flash/standard/pro/ultra) + task-master(任务管理,core/standard/all)
```

## 三层架构

```
骨架层 (methodology)  → P0 路由集(6) L1×4+L2门控×2 + CORE铁律 + 审查路由 + MCP basic
执行层 (capability)   → 阶段 skill + agent + domain rules（按需 reactive）
护栏层 (guardrails)   → 安全/治理/效率 hook（骨架级4 + 按需级4）
                        + 学习 loop（Stop/PreCompact 触发）
```

## 五阶段处理流程

```
用户输入 → ①规划(/discuss) → ②规格(/plan) → ③执行(/execute) → ④验证(/verify) → ⑤学习(/compact)
              │                  │               │                 │                  │
          grill→HARD-GATE     spec-valid      主会话直接执行      gstack审查       pattern提取
          Red Flags表        OpenSpec格式     原子任务(2-5min)    quality-gate    claude-mem SSOT
          一次一问            三轨互斥      SDD/TDD 仅显式触发    反合理化         上下文压缩
```

> **③ 执行默认不启用 TDD/SDD（v10.15）**：仅用户显式要求（TDD/测试先行/子Agent派发）才 Read `test-driven-development` / `subagent-driven-development`。判定与 grill 规则 SSOT → `skills/task-triage/SKILL.md`。

---

## 五柱声明

| 柱          | 来源                  | 职责                                    | 骨架                        | 执行                                                                                       | 护栏                                                   |
| ----------- | --------------------- | --------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| Superpowers | obra/superpowers      | 方法论 + P0 + HARD-GATE                 | P0×6                        | brainstorming→writing-plans(原子)→execute→verify（TDD 仅显式触发）                         | def-in-depth + 反合理化                                |
| GSD Redux   | open-gsd/gsd-core     | 上下文工程 + 阈值 (原 gsd-build 已归档) | 三级阈值 + 制品优先         | 上下文工程能力（正文在 rules/CONTEXT.md，非已删同名 skill；subagent 两阶段审查仅显式触发） | read-before-edit + canonical-source + trust-but-verify |
| OpenSpec    | Fission-AI/OpenSpec   | 规格格式 core OPSX                      | 三轨互斥                    | spec-validation + opsx 全链                                                                | spec-reviewer门控                                      |
| gstack      | garrytan/gstack       | 审查角色                                | 审查路由 6+3+1（本地）+ autoplan/ship | eng/ceo/designer/dx/qa/security（只找问题）；修改→change-implementer | browser-qa + quality-gate                              |
| claude-mem  | thedotmack/claude-mem | 跨会话记忆                              | SSOT 渐进式披露             | mem-search/timeline/knowledge-agent                                                        | MEMORY.md↔claude-mem统一 + Chroma                      |

---

## 规模约束

| 类型         | v11    | 说明                                                                                                                                                                                   |
| ------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 全局 skills  | 36     | P0 路由集 6 + supplement 30（v11: 45→36，6 降级 catalog + 3 删并）                                                                                                                     |
| 全局 agents  | 17     | core 7 + 审查 6 + 补全 3 + 跨模型 1（v11.4.11：16→17，补 change-implementer）                                                                                                             |
| 全局 rules   | 10     | alwaysApply 1(CORE) + model_decision 8 + glob 1（FRONTEND；不含 README；v11: DESIGN/BESTPRACTICE 并入）                                                                                |
| CLAUDE.md    | ≤200   | 唯一 L0 入口（v11 并入 ROUTER）：路由链 + P0 + 五阶段 + 铁律                                                                                                                           |
| 全局 hooks   | 19     | 注册激活 19 + 未注册 5 + 分发器 2（`_editor_*`）；Cursor Guard 运行时 23（v1.2.11，resume 审查不计入）                                                                                    |
| 全局 MCP     | 4 常驻 | codegraph + CRG + serena + grep；plugin（context7/exa/playwright/firecrawl）不计入常驻 MCP；debug/fsaccess/ops 见 mcp-configs/                                                          |
| 全局 plugins | 18     | installed_plugins 18；settings enabledPlugins 全量显式登记（v11.4.3 补 claude-hud=true / exa=false，禁双挂）：启用8 / 禁用10                                                                                                                           |
| 可选外部     | 2      | deer-flow 2.0 + task-master MCP                                                                                                                                                        |

---

## P0 路由集（6）= L1×4 + L2 门控×2

| Skill                          | 等级        | 触发                        | 阶段   |
| ------------------------------ | ----------- | --------------------------- | ------ |
| using-superpowers              | L1 常驻     | 会话开始、分类路由          | 全阶段 |
| task-triage                    | L1 常驻     | 新任务两大类+关联需改≤2判定 | 全阶段 |
| change-impact-analysis         | L1 按需全文 | 任何修改意图                | 全阶段 |
| brainstorming                  | L1 常驻     | 非简单 ①规划                | ①      |
| verification-before-completion | L2 门控     | ④验收                       | ④      |
| systematic-debugging           | L2 门控     | Bug/测试失败                | ③调试  |

**Cursor**：L2/L3 supplement 用 `disable-model-invocation: true` + 显式 Read。
**Claude Code**：`layer: skeleton/supplement` + using-superpowers 路由 Read。

### 加载等级 L0–L3（MANIFEST SSOT；历史 L4 已并入 L3_dispatch）

| 等级 | 内容                                                                                           |
| ---- | ---------------------------------------------------------------------------------------------- |
| L0   | CLAUDE.md（v11 并入 ROUTER）+ CORE                                                             |
| L1   | using-superpowers, task-triage, change-impact-analysis, brainstorming                          |
| L2   | 阶段门控：writing-plans, spec-validation, executing-plans, verification, debugging             |
| L3   | 其余 skills（含 subagent-driven-development 显式触发）+ agents(Task)/MCP/claude-mem/lazy rules |

## Workflow Skills

**Superpowers 12**：using-superpowers, brainstorming, writing-plans(原子), executing-plans, verification-before-completion, systematic-debugging, test-driven-development, subagent-driven-development(两阶段审查), using-git-worktrees, receiving-code-review, requesting-code-review, finishing-a-development-branch（writing-skills 已并入 skill-creator 前言）

**扩展 4（v11）**：autoplan, design-pipeline, ship, structured-artifacts（office-hours/browser-qa 降级 catalog；context-engineering 删除，rules/CONTEXT.md 为唯一正文）

**Meta 5**：memory-compression, spec-validation, karpathy-guidelines, caveman-compress, change-impact-analysis

**Mattpocock 2**：triage, improve-codebase-architecture

**项目洞察 1**：codegraph（R17 常驻）；codebase-memory **已禁用**（v10.10+，全盘索引爆 CPU/内存；UA removed v10.5）

---

## 执行层：SDD + TDD 组合（默认关闭，显式触发 — v10.15）

> 用户未明确要求时**不执行** TDD/SDD：默认非简单任务走 ①-⑤ 骨架由主会话直接执行。
> 以下模式仅在用户显式要求（TDD/测试先行/子Agent派发）时启用。

```
模式一 SDD: spec → writing-plans(原子) → subagent(两阶段审查) → verify
模式二 TDD: RED(失败测试) → GREEN(最小通过) → REFACTOR → verify
模式三 组合: writing-plans → 每个task: RED→GREEN→REFACTOR → 两阶段审查 → verify
```

---

## 核心 Agents (7)

| Agent                | 阶段  |
| -------------------- | ----- |
| planner              | ①规划 |
| code-reviewer        | ④验证 |
| build-error-resolver | ③执行 |
| architect            | ①规划 |
| spec-reviewer        | ②规格 |
| agentic-orchestrator | ③执行 |
| code-explorer        | ③执行 |

## gstack 审查 6+3+1（v11.4.11 引入 change-implementer；v11.4.12 一次找齐+每轮全新开审）

**审查 (skeleton)**：eng-reviewer, ceo-reviewer, designer, dx-reviewer, qa, security-reviewer（深度模式=原 cso 全量审计）
**补全 (supplement)**：sre, doc-writer, change-implementer
**跨模型**：codex-reviewer
**catalog 按需变体**：ios-specialist, design-shotgun, pair-agent, land-and-deploy, performance-engineer（release-engineer→skill/ship；design-engineer→skill/design-pipeline；product-manager 删除）

---

## 变更彻底性保障

> 详见 `rules/CORE.md` 变更彻底性保障章节

```
变更前: codegraph_impact(target) + Grep 全项目 + MANIFEST depends_on → 清单
变更中: 按依赖图顺序 → Read→Edit→Read
变更后: Grep 残留引用 → 构建/类型/Lint → MANIFEST 一致性
```

---

## 护栏层

```
骨架级 (always-on)
├─ pre-bash-guard → 阻断危险命令
├─ pre-read-before-edit → 编辑前已读
├─ pre-manifest-validator → 归属冲突检测
└─ post-secret-detector → 密钥泄露检测

按需级 (profile控制)
├─ pre-rtk-rewrite → Shell token优化
├─ pre-context-injector → 会话缓存注入
├─ post-edit-format → 编辑后格式化
└─ stop-verification-gate → 完成验证硬门（exit 2 回灌）+ /verify或/ship时

学习loop (Stop/PreCompact)
├─ pre-compact-state → 压缩前快照 → ~/.claude/state.json
├─ stop-context-monitor → GateGuard（loop/scope/cost）
├─ stop-session-summary → 会话摘要
├─ stop-readme-updater → README更新
└─ pattern提取 → ⑤学习默认 claude-mem observation（`catalog/skills/instinct-learning` v11 降级，按需复制）

# codegraph 索引刷新：v1.5 起 MCP server 原生监听自动同步（v11 退役 post-codegraph-sync / stop-knowledge-graph-sync）
```

---

## 规格三轨（互斥）

| 轨道            | 路径                     | 场景                                   | 入口                                    |
| --------------- | ------------------------ | -------------------------------------- | --------------------------------------- |
| OpenSpec /opsx: | `openspec/changes/<id>/` | 功能变更/brownfield                    | /opsx:propose → verify → sync → archive |
| GSD Redux       | `.planning/phases/`      | 大功能多阶段                           | /plan                                   |
| 轻量            | `spec/<project>/`        | 简单(task-triage判定=关联需改≤2)小功能 | /plan                                   |

---

## ECC cherry-pick（v10，无插件）

| 吸收                      | 位置                                      |
| ------------------------- | ----------------------------------------- |
| module_resolver.conflicts | MANIFEST.yaml                             |
| LOCAL_HOOK_PROFILE        | hooks/README.md                           |
| GateGuard 概念            | stop-context-monitor, pre-suggest-compact |

**禁止**安装 everything-claude-code 插件（duplicate hooks）。

---

## MCP 分组（plugin 优先；chrome-devtools 默认关）

| 分组       | 服务器                                               | 加载                                   |
| ---------- | ---------------------------------------------------- | -------------------------------------- |
| 本地代码   | codegraph, code-review-graph, serena                 | `.mcp.json` 常驻                       |
| 远端探索   | grep                                                 | `.mcp.json` 常驻                       |
| Plugins    | context7, exa, playwright                            | `settings.json` enabledPlugins=true    |
| Plugins 默认关 | chrome-devtools, github, firecrawl                 | plugin=false；不写 MCP                 |
| debug      | chrome-devtools                                      | `mcp-configs/debug.json` 按需 merge    |
| fsaccess   | fs                                                   | `mcp-configs/fsaccess.json` 按需 merge |
| ops        | redis, sqlite, docker, postgres                      | `mcp-configs/ops.json` 按需 merge      |
| collab     | figma, linear, notion, slack                         | `mcp-configs/collab.json`（声明）      |

本地代码三工具分工（codegraph 探索主位 / serena 符号级编辑 / code-review-graph 变更后审查）→ [rules/MCP.md](rules/MCP.md) §4

已删除：`aider-repo-map`、`sequential-thinking`（不要加回）。

Cursor 侧 → [docs/CURSOR_MCP_PROFILE.md](docs/CURSOR_MCP_PROFILE.md)（v11：RUNTIME_PLAYBOOK 已并入 CLAUDE.md / rules/CONTEXT.md / rules/MCP.md）

权威 → `.mcp.json` | 分组 → `mcp/servers.json`

---

## 防互博速查

| 场景        | Owner                                                           | 禁止                                              |
| ----------- | --------------------------------------------------------------- | ------------------------------------------------- |
| 计划        | skill/writing-plans                                             | hook/pre-task-planner, agent/agentic-orchestrator |
| 审查        | requesting/receiving-code-review                                | 独立 code-review skill                            |
| 记忆        | plugin/claude-mem                                               | agent/context-manager                             |
| Shell token | hook/pre-rtk-rewrite                                            | skill 重复压缩                                    |
| 输出 token  | skill/caveman-compress                                          | RTK 压缩 agent 文本                               |
| 功能 spec   | openspec/changes/                                               | .planning 同功能重写                              |
| 测试覆盖    | agent/eng-reviewer                                              | agent/qa (QA 只管边界/回归)                       |
| pattern提取 | skills/claude-mem-maintenance（instinct-learning 降级 catalog） | hook/stop-pattern-extraction (v1已停用)           |

---

## 29 仓库完整映射（+plugins-official = 29 编号项，含 19b 子项）

### 五柱 (5)

| #   | 仓库                  | 吸收                                                                                                     | 落地                                                                 |
| --- | --------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1   | obra/superpowers      | 14技能+HARD-GATE+Red Flags+原子任务+两阶段审查                                                           | skills/×12（v11: writing-skills 并入 skill-creator）, hooks/         |
| 2   | open-gsd/gsd-core     | 三级阈值+read-before-edit+canonical-source+trust-but-verify+连续执行 (原 gsd-build/get-shit-done 已归档) | rules/CONTEXT, rules/WORKFLOW                                        |
| 3   | Fission-AI/OpenSpec   | proposal→spec→tasks+brownfield+archive                                                                   | templates/openspec/, spec-validation, commands/propose+apply+archive |
| 4   | garrytan/gstack       | 本地收敛：6审查+3补全+1跨模型（上游曾 5审查+7补全）+浏览器QA+autoplan/ship                                    | agents/×9 + catalog/agents/×5（v11 收敛）                            |
| 5   | thedotmack/claude-mem | 渐进式披露+向量搜索+6hook SSOT+15技能                                                                    | plugin/claude-mem                                                    |

### 结构格式 (6)

| #   | 仓库                        | 吸收                                                | 落地                                                          |
| --- | --------------------------- | --------------------------------------------------- | ------------------------------------------------------------- |
| 6   | affaan-m/ECC                | MANIFEST+agent路由+instinct-learning v2             | MANIFEST.yaml（含 harness 节，v11 吸收 agent.yaml）, catalog/ |
| 7   | anthropics/skills           | SKILL.md格式标准+跨平台                             | skills//SKILL.md                                              |
| 8   | shanraisshan/best-practice  | 15类别200+行                                        | rules/GOVERNANCE 最佳实践详参章（v11 并入）                   |
| 9   | forrestchang/karpathy       | 四原则+实施规则+量化测试+弱命令转换表               | rules/CORE, karpathy-guidelines                               |
| 10  | mattpocock/skills           | triage(状态机+P0-P3)+架构改进(8术语+删除测试+Grill) | skills/triage, improve-codebase-architecture                  |
| 11  | VoltAgent/awesome-design-md | 9章节结构+73品牌+零依赖                             | rules/FRONTEND 设计系统节（v11 并入）, templates/DESIGN.md    |

### 优化工具 (4)

| #   | 仓库                          | 吸收                             | 落地                      |
| --- | ----------------------------- | -------------------------------- | ------------------------- |
| 12  | rtk-ai/rtk                    | Rust CLI 60-90%压缩+100+命令预置 | hooks/pre-rtk-rewrite     |
| 13  | JuliusBrussee/caveman         | 四级压缩+仅压输出                | skill/caveman-compress    |
| 14  | github/github-mcp-server      | 80+工具+17工具集                 | 不常驻；GitHub 操作用 `gh` CLI |
| 15  | anthropics/claude-code-action | 4后端CI+结构化JSON               | templates/github-actions/ |

### 编排增强 (4)

| #   | 仓库                           | 吸收                                                          | 落地                          |
| --- | ------------------------------ | ------------------------------------------------------------- | ----------------------------- |
| 16  | eyaltoledano/task-master       | PRD→结构任务+3级工具裁剪(core/standard/all)+~70% token减少    | 按需MCP                       |
| 17  | nextlevelbuilder/ui-ux-pro-max | 67风格+161色板+99UX                                           | catalog/skills/ui-ux-pro-max/ |
| 29  | DeusData/codebase-memory-mcp   | 知识图谱 L4 架构/ADR/变更                                     | optional-dev.json             |
| 18  | zilliztech/claude-context      | archived_redirect → cbm                                       | 仅历史卡                      |
| 19  | bytedance/deer-flow            | LangGraph编排+9层Middleware+Sandbox+claude-to-deerflow bridge | WORKFLOW.md + skill 指针      |
| 19b | ruvnet/ruflo                   | 蜂群拓扑+HNSW向量记忆+SONA自学习（仅概念参考）                | WORKFLOW.md 概念              |

### 参考索引 (5)

| #   | 仓库                             | 吸收                                | 落地                                     |
| --- | -------------------------------- | ----------------------------------- | ---------------------------------------- |
| 20  | ComposioHQ/awesome-claude-skills | 1000+技能索引+渐进式加载            | catalog/ 索引                            |
| 21  | hesreallyhim/awesome-claude-code | 配置范式+工具发现                   | 外链索引                                 |
| 22  | x1xhlol/system-prompts           | 30+提示词比较+实证分析              | rules/GOVERNANCE 系统提示词实证段（v11） |
| 23  | Chalarangelo/30-seconds-of-code  | 信息架构参考（不直接引入）          | catalog 参考                             |
| 24  | ruvnet/ruflo                     | 制品持久化模式（蜂群拓扑/HNSW排除） | WORKFLOW.md                              |

### 安全 (3)

| #   | 仓库                            | 吸收                   | 落地            |
| --- | ------------------------------- | ---------------------- | --------------- |
| 25  | trailofbits/claude-code-config  | /sandbox+deny+三层防御 | SECURITY.md §11 |
| 26  | marc-shade/claude-code-security | 渐进硬化checklist      | SECURITY.md §14 |

### 项目洞察 (1)

| #   | 仓库                   | 吸收                                                                                   | 落地                                   |
| --- | ---------------------- | -------------------------------------------------------------------------------------- | -------------------------------------- |
| 27  | colbymchenry/codegraph | 预索引知识图谱MCP，官方均值 ~16%成本/~47%token/~58%工具调用/~22%更快；MCP默认4工具(F1) | .mcp.json (optional), rules/CONTEXT.md |

### 插件分发 (1)

| #   | 仓库                               | 吸收                                                | 落地                                          |
| --- | ---------------------------------- | --------------------------------------------------- | --------------------------------------------- |
| 29  | anthropics/claude-plugins-official | 官方市场分发 SSOT；gitCommitSha pinning；LSP 族按需 | plugins/installed_plugins.json, settings.json |

---

## Plugins（18 安装；enabledPlugins 启用8 / 禁用10，以 settings.json 为准）

> v10.17 按 `plugins/installed_plugins.json` × `settings.json.enabledPlugins` 实测重写。
> 此前本表长期停留在旧快照（声称 15 启用），与运行态严重不符。

| Plugin                     | 状态 | 提供                      | 说明                                                     |
| -------------------------- | ---- | ------------------------- | -------------------------------------------------------- |
| superpowers 6.2.0          | ✅   | SessionStart + 方法论技能 | 五柱之一，随上游自动更新                                 |
| claude-mem 13.13.1         | ✅   | 6 hooks + 记忆技能        | 五柱之一（R18 记忆优先）                                 |
| code-review                | ✅   | 审查技能                  | 与 eng-reviewer 互补                                     |
| commit-commands            | ✅   | Git 快捷命令              | —                                                        |
| frontend-design            | ✅   | 前端设计                  | —                                                        |
| skill-creator              | ✅   | 技能创建                  | —                                                        |
| claude-md-management 1.0.0 | ✅   | CLAUDE.md 维护            | 早期因「防覆盖」禁用，现已启用                           |
| chrome-devtools-mcp 1.6.0  | ❌   | Chrome DevTools           | v10.17 浏览器按需化；需要时走 `mcp-configs/debug.json`   |
| context7                   | ✅   | 技术文档                  | Claude/Cursor **plugin**（禁止再写 `.mcp.json`）         |
| firecrawl 1.0.9            | ✅   | 网页抓取                  | Claude **plugin**（不写 MCP）；Cursor 无常驻则降级 Exa   |
| github                     | ❌   | GitHub 集成               | plugin=false 且不写 MCP；PR/Issue 用 `gh` CLI            |
| playwright                 | ✅   | 浏览器自动化              | Claude/Cursor **plugin**；Cursor UI 核验优先内置浏览器   |
| security-guidance 2.0.6    | ❌   | 安全规则                  | 由 `rules/SECURITY.md` 承担                              |
| typescript-lsp 1.0.0       | ❌   | TS LSP                    | 由 serena LSP 能力承担                                   |
| feature-dev                | ❌   | 功能开发                  | 与五阶段流程重叠                                         |
| ralph-loop                 | ❌   | 自动循环                  | 与五阶段冲突                                             |
| claude-hud 0.6.0           | ✅   | 上下文 HUD 状态条         | v11.4.3 enabledPlugins=true                              |
| exa 3.4.0                  | ✅   | Exa 搜索                  | v11.4.5 **plugin**（禁止与 MCP 双挂；不写 `.mcp.json`）  |

> 归属：SessionStart→插件 | 守卫/质量门→hooks | 审查→agents。enabledPlugins 与 MANIFEST 对齐（启用8/禁用10 以 settings.json 为准）。hooks 仅 superpowers / claude-mem。
> 同名 skill：本地精简版覆盖插件版（token 省 45-74%，中文适配）。

---

## 同步（v11.1 多编辑器 1+N）

| 端                               | 方式                                                                             |
| -------------------------------- | -------------------------------------------------------------------------------- |
| Claude Code                      | 原生读 `~/.claude`，零同步                                                       |
| Cursor：根文件 / skills / agents | 软链接 + Junction（sync.ps1 v20，清单/常量单源 config/sync-manifest.json）       |
| Cursor：rules                    | local plugin 实体 .mdc（唯一规则通道）                                           |
| qoder-cn / trae-cn               | 根文件 6 软链 + `rules/*.mdc` / `user_rules/*.md`（实体+`.claude-managed` 台账） |
| workbuddy                        | 仅 `CLAUDE.md` + `skills/` 联接（SOUL/USER 自有命名空间禁触，跳根索引；home 缺席跳过） |
| DSH / OpenCode                   | **适配层**（`sync-manifest.json` `harnesses`）：便携 CLI/R20/图谱插件；**禁止** CLAUDE.md 覆盖 AGENTS.md |
| hooks/, commands/, MCP, plugins  | 不同步（TRAE R19 守卫为独立通道：AppData hooks_env 副本）                        |

---

## 变更史

> v11 起版本变更摘要外置 → [CHANGELOG.md](CHANGELOG.md)（v9.0 起全量）。

---

> 版本：11.4.13 | 日期：2026-09-03 | 五柱×五阶段×三横切 | 场景路由 YAML + harness 能力图 | MCP 常驻 4 | 审前双图 + inherit 并行审查（禁倍率档） | 图谱保鲜硬门 | 审查一次找齐 | L0–L3 | 同步 1+N + DSH/OpenCode 适配层 | R20
