# SPEC.md — 配置法典索引

> CLAUDE.md 为路由层（≤200行）；本文件为法典索引；变更史 → `CHANGELOG.md`。
> 版本：13.0.2 | 五柱×五阶段×三横切 | **配置驱动主干 `config/workflow.yaml`（模型/推理强度无关）**：阶段 entry/exit 门 × 轨道 × 完成定义（每条轨道独立审查必过，两道关：符合预期要求 + 原功能保持）× 审查 ≤3 轮/七维/路由 → `scripts/workflow.py render` 派生 + lint 拦模型绑定，V21 防漂移；模型与推理强度由会话/settings/调用方决定 + L0–L3 分级加载 + MCP 常驻 5 项（codegraph/CRG/serena/everything/grep）+ 图谱三时点 + 审查只找问题、修改走 change-implementer + 配置/文档/注释必须同步 + 工具链 SSOT `config/toolchain.yaml`（pwsh 7.5 / pnpm 11；缺工具 BLOCKED）+ TDD/SDD 显式触发 + 多编辑器同步 1+N | UA removed | cbm 已禁用

---

## 架构公式

```
RUNTIME  = Superpowers(方法论) + GSD Redux(上下文) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
FORMAT   = ECC模式(cherry-pick) + anthropics/skills(格式) + best-practice(实证)
REVIEW   = 独立审查者 7（eng 必审 + ceo/designer/dx/qa/security/cross-model 按路由）；完成 = 审查 PASS（两道关）
OPTIMIZE = RTK(shell token) + caveman(输出token)
INSIGHT  = codegraph(R17 常驻) + codebase-memory(已禁用：全盘索引爆 CPU/内存，codegraph 全权替代) + Exa/Firecrawl(外部调研)  # UA removed v10.5
SPINE    = config/workflow.yaml（stages/tracks/completion/quality/review；无模型/推理强度）→ scripts/workflow.py render → agents/commands/CLAUDE.md/quality_gates.json；lint 全仓拦模型绑定
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

> v13：阶段、轨道（simple / bug / non_simple / research）、每阶段 entry/exit 门、完成定义（`completion`：每条轨道独立审查必过，耗尽 = BLOCKED）全部定义在 `config/workflow.yaml`；派生表见 `CLAUDE.md`「工作流主干」与 `docs/DEV_FLOW.md`。本文件不再复写流程图。
> 一次通过契约：`quality.definition_of_ready`（③执行前）+ `quality.self_check`（交审前，与审查者同一份七维）。

> **③ 执行默认不启用 TDD/SDD（v10.15）**：仅用户显式要求（TDD/测试先行/子Agent派发）才 Read `test-driven-development` / `subagent-driven-development`。判定与 grill 规则 SSOT → `skills/task-triage/SKILL.md`。

---

## 五柱声明

| 柱          | 来源                  | 职责                                    | 骨架                        | 执行                                                                                       | 护栏                                                   |
| ----------- | --------------------- | --------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| Superpowers | obra/superpowers      | 方法论 + P0 + HARD-GATE                 | P0×6                        | brainstorming→writing-plans(原子)→execute→verify（TDD 仅显式触发）                         | def-in-depth + 反合理化                                |
| GSD Redux   | open-gsd/gsd-core     | 上下文工程 + 阈值 (原 gsd-build 已归档) | 三级阈值 + 制品优先         | 上下文工程能力（阈值在 rules/CORE.md，压缩在 skill/memory-compression；subagent 两阶段审查仅显式触发） | read-before-edit + canonical-source + trust-but-verify |
| OpenSpec    | Fission-AI/OpenSpec   | 规格格式 core OPSX                      | 三轨互斥                    | spec-validation + opsx 全链                                                                | spec-validation 门控                                   |
| gstack      | garrytan/gstack       | 审查角色                                | 审查路由（workflow.yaml review.routing）+ ship | eng/ceo/designer/dx/qa/security/cross-model（只找问题）；修改→change-implementer | browser-qa + quality-gate                              |
| claude-mem  | thedotmack/claude-mem | 跨会话记忆                              | SSOT 渐进式披露             | mem-search/timeline/knowledge-agent                                                        | MEMORY.md↔claude-mem统一 + Chroma                      |

---

## 规模约束

| 类型         | v13    | 说明                                                                                                                                                                                   |
| ------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 全局 skills  | 26     | L1×4 + L2×5 + L3×17（v13: 35→26，去向见 skills-INDEX）                                                                                                                     |
| 全局 agents  | 9      | 阶段角色 2（planner / change-implementer）+ 独立审查者 7；agent 不声明模型/推理强度，继承调用方                                                                                                             |
| 全局 rules   | 6      | alwaysApply 1(CORE) + model_decision 5（不含 README；领域规则 → catalog/rules）                                                                                                |
| CLAUDE.md    | ≤200   | 唯一 L0 入口（v11 并入 ROUTER）：路由链 + P0 + 五阶段 + 铁律                                                                                                                           |
| 全局 hooks   | 18     | 注册激活 18 + 未注册 1 + 分发器 2（v12 删 4 个未注册 hook）（`_editor_*`）；v11.5 `r20-capture` SubagentStop；Cursor Guard 运行时 23（v1.2.17）                                                              |
| 全局 MCP     | 5 常驻 | 本地代码3 + everything + grep；debug/fsaccess/ops 见 mcp-configs/                                                                                                                      |
| 全局 plugins | 18     | installed_plugins 18；开关 SSOT → `rules/MCP.md` 验证清单（context7/exa/playwright/firecrawl=true；chrome-devtools/github=false；不写 MCP）                                                                                                                           |
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

**Superpowers 12**：using-superpowers, brainstorming, writing-plans(原子), executing-plans, verification-before-completion, systematic-debugging, test-driven-development, subagent-driven-development(两阶段审查), using-git-worktrees, receiving-code-review, requesting-code-review, finishing-a-development-branch（v12 起为指向 ship 的薄壳；writing-skills 已并入 skill-creator 前言）

**支撑 12（v13）**：spec-validation, memory-compression, caveman-compress, claude-mem-maintenance, deep-research, adr-management, design-pipeline, ship, git-workflow, workstream-management, skill-creator, skill-reviewer

**v13 删除 9**：karpathy-guidelines（并入 CORE 开发习惯）、triage（并入 systematic-debugging 分诊）、autoplan、structured-artifacts、improve-codebase-architecture、code-refactoring、frontend-library-advisor、frontend-design-pattern-applier、test-edge-case-analyzer

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

## Agents (9)

| Agent | 角色 |
| --- | --- |
| planner | ②规格 阶段角色 |
| change-implementer | ③执行 阶段角色（唯一修改者） |
| eng-reviewer | 独立审查（每条轨道必审） |
| ceo-reviewer / designer / dx-reviewer / qa / security-reviewer | 独立审查（按 review.routing 追加；security 深度模式=原 cso） |
| cross-model-reviewer | 独立审查（用户要求跨模型时；模型由调用方选） |

**catalog 按需变体**：ios-specialist, design-shotgun, pair-agent, land-and-deploy, performance-engineer。v13 删除：code-explorer, architect, agentic-orchestrator, build-error-resolver, spec-reviewer, sre, doc-writer（去向 → agents/README.md）。

---

## 变更彻底性保障

> 详见 `rules/CORE.md`「开发习惯」与 `skills/change-impact-analysis`

```
变更前: CRG get_impact_radius（有图）+ codegraph_explore blast-radius + Grep + MANIFEST depends_on → 清单
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

按需级 (LOCAL_HOOK_PROFILE 控制)
├─ pre-rtk-rewrite → Shell token优化
├─ pre-context-injector → 会话缓存注入
├─ post-edit-format → 编辑后格式化
└─ stop-verification-gate → 完成验证硬门（exit 2 回灌）+ /verify或/ship时

学习loop (Stop/PreCompact)
├─ pre-compact-state → 压缩前快照 → ~/.claude/state.json
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
| GateGuard 概念            | v12 已删（Claude 原生 autoCompact + Cursor Guard 阈值覆盖） |

**禁止**安装 everything-claude-code 插件（duplicate hooks）。与 voidtools `everything` MCP（elis132/everything-mcp）不是同一物。

---

## MCP 分组（plugin 优先；chrome-devtools 默认关）

| 分组       | 服务器                                               | 加载                                   |
| ---------- | ---------------------------------------------------- | -------------------------------------- |
| 本地代码   | codegraph, code-review-graph, serena                 | `.mcp.json` 常驻                       |
| 本机文件名 | everything（elis132/everything-mcp；仅 Windows）     | `.mcp.json` 常驻；勿与 marketplace plugin 双挂 |
| 远端探索   | grep                                                 | `.mcp.json` 常驻                       |
| Plugins    | context7, exa, playwright, firecrawl             | `settings.json` enabledPlugins=true；不写 MCP |
| Plugins 默认关 | chrome-devtools, github                        | plugin=false；不写 MCP；github 用 `gh` CLI |
| debug      | chrome-devtools                                      | `mcp-configs/debug.json` 按需 merge    |
| fsaccess   | fs                                                   | `mcp-configs/fsaccess.json` 按需 merge |
| ops        | redis, sqlite, docker, postgres                      | `mcp-configs/ops.json` 按需 merge      |
| collab     | figma, linear, notion, slack                         | `mcp-configs/collab.json`（声明）      |

本地代码三工具 + everything 分工（codegraph 探索主位 / serena 符号级编辑 / CRG 影响面审查 / everything 本机文件名）→ [rules/MCP.md](rules/MCP.md) §4

已删除：`aider-repo-map`、`sequential-thinking`（不要加回）。

Cursor 侧 → [docs/CURSOR_MCP_PROFILE.md](docs/CURSOR_MCP_PROFILE.md)（RUNTIME_PLAYBOOK 已并入 CLAUDE.md / rules/CORE.md / rules/MCP.md）

权威 → `.mcp.json` | 分组 → `mcp/servers.json`

---

## 防互博速查

| 场景        | Owner                                                           | 禁止                                              |
| ----------- | --------------------------------------------------------------- | ------------------------------------------------- |
| 计划        | skill/writing-plans                                             | hook/pre-task-planner                             |
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
| 2   | open-gsd/gsd-core     | 三级阈值+read-before-edit+canonical-source+trust-but-verify+连续执行 (原 gsd-build/get-shit-done 已归档) | rules/CORE, config/workflow.yaml                                     |
| 3   | Fission-AI/OpenSpec   | proposal→spec→tasks+brownfield+archive                                                                   | templates/openspec/, spec-validation, commands/propose+apply+archive |
| 4   | garrytan/gstack       | 本地收敛：7 独立审查者 + 修改者（上游曾 5审查+7补全）+浏览器QA+ship                                         | agents/×9 + catalog/agents/×5                                        |
| 5   | thedotmack/claude-mem | 渐进式披露+向量搜索+6hook SSOT+15技能                                                                    | plugin/claude-mem                                                    |

### 结构格式 (6)

| #   | 仓库                        | 吸收                                                | 落地                                                          |
| --- | --------------------------- | --------------------------------------------------- | ------------------------------------------------------------- |
| 6   | affaan-m/ECC                | MANIFEST+agent路由+instinct-learning v2             | MANIFEST.yaml（含 harness 节，v11 吸收 agent.yaml）, catalog/ |
| 7   | anthropics/skills           | SKILL.md格式标准+跨平台                             | skills//SKILL.md                                              |
| 8   | shanraisshan/best-practice  | 15类别200+行                                        | rules/CORE 开发习惯（v13 精简）                               |
| 9   | forrestchang/karpathy       | 四原则+实施规则+量化测试+弱命令转换表               | rules/CORE 开发习惯                                           |
| 10  | mattpocock/skills           | triage(状态机+P0-P3)+架构改进(8术语+删除测试+Grill) | skills/systematic-debugging 分诊节（v13）                     |
| 11  | VoltAgent/awesome-design-md | 9章节结构+73品牌+零依赖                             | catalog/rules/RULES_FRONTEND.md, templates/DESIGN.md          |

### 优化工具 (4)

| #   | 仓库                          | 吸收                             | 落地                      |
| --- | ----------------------------- | -------------------------------- | ------------------------- |
| 12  | rtk-ai/rtk                    | Rust CLI 60-90%压缩+100+命令预置 | hooks/pre-rtk-rewrite     |
| 13  | JuliusBrussee/caveman         | 四级压缩+仅压输出                | skill/caveman-compress    |
| 14  | github/github-mcp-server      | 80+工具+17工具集                 | .mcp.json (gh)            |
| 15  | anthropics/claude-code-action | CI 审查+结构化JSON（模型由 CI 配置） | templates/github-actions/ |

### 编排增强 (4)

| #   | 仓库                           | 吸收                                                          | 落地                          |
| --- | ------------------------------ | ------------------------------------------------------------- | ----------------------------- |
| 16  | eyaltoledano/task-master       | PRD→结构任务+3级工具裁剪(core/standard/all)+~70% token减少    | 按需MCP                       |
| 17  | nextlevelbuilder/ui-ux-pro-max | 67风格+161色板+99UX                                           | catalog/skills/ui-ux-pro-max/ |
| 29  | DeusData/codebase-memory-mcp   | 知识图谱 L4 架构/ADR/变更                                     | optional-dev.json             |
| 18  | zilliztech/claude-context      | archived_redirect → cbm                                       | 仅历史卡                      |
| 19  | bytedance/deer-flow            | LangGraph编排+9层Middleware+Sandbox+claude-to-deerflow bridge | catalog/skills/claude-to-deerflow |
| 19b | ruvnet/ruflo                   | 蜂群拓扑+HNSW向量记忆+SONA自学习（仅概念参考）                | 仅概念参考                    |

### 参考索引 (5)

| #   | 仓库                             | 吸收                                | 落地                                     |
| --- | -------------------------------- | ----------------------------------- | ---------------------------------------- |
| 20  | ComposioHQ/awesome-claude-skills | 1000+技能索引+渐进式加载            | catalog/ 索引                            |
| 21  | hesreallyhim/awesome-claude-code | 配置范式+工具发现                   | 外链索引                                 |
| 22  | x1xhlol/system-prompts           | 30+提示词比较+实证分析              | 参考（v13 GOVERNANCE 删除）              |
| 23  | Chalarangelo/30-seconds-of-code  | 信息架构参考（不直接引入）          | catalog 参考                             |
| 24  | ruvnet/ruflo                     | 制品持久化模式（蜂群拓扑/HNSW排除） | rules/CORE R13                           |

### 安全 (3)

| #   | 仓库                            | 吸收                   | 落地            |
| --- | ------------------------------- | ---------------------- | --------------- |
| 25  | trailofbits/claude-code-config  | /sandbox+deny+三层防御 | SECURITY.md §11 |
| 26  | marc-shade/claude-code-security | 渐进硬化checklist      | SECURITY.md §14 |

### 项目洞察 (1)

| #   | 仓库                   | 吸收                                                                                   | 落地                                   |
| --- | ---------------------- | -------------------------------------------------------------------------------------- | -------------------------------------- |
| 27  | colbymchenry/codegraph | 预索引知识图谱MCP，官方均值 ~16%成本/~47%token/~58%工具调用/~22%更快；MCP默认4工具(F1) | .mcp.json, rules/CORE.md R17           |

### 插件分发 (1)

| #   | 仓库                               | 吸收                                                | 落地                                          |
| --- | ---------------------------------- | --------------------------------------------------- | --------------------------------------------- |
| 29  | anthropics/claude-plugins-official | 官方市场分发 SSOT；gitCommitSha pinning；LSP 族按需 | plugins/installed_plugins.json, settings.json |

---

## Plugins（18 安装；启用/禁用以 `rules/MCP.md` 验证清单与 `settings.json` 为准）

> 同名能力只留 plugin，禁止再写入 `.mcp.json`。现行 Claude：context7 / exa / playwright / firecrawl plugin=true；chrome-devtools / github plugin=false。

| Plugin                     | 状态 | 提供                      | 说明                                                     |
| -------------------------- | ---- | ------------------------- | -------------------------------------------------------- |
| superpowers 6.3.0          | ✅   | SessionStart + 方法论技能 | 五柱之一，随上游自动更新                                 |
| claude-mem 13.13.1         | ✅   | 6 hooks + 记忆技能        | 五柱之一（R18 记忆优先）                                 |
| code-review                | ✅   | 审查技能                  | 与 eng-reviewer 互补                                     |
| commit-commands            | ✅   | Git 快捷命令              | —                                                        |
| frontend-design            | ✅   | 前端设计                  | —                                                        |
| skill-creator              | ✅   | 技能创建                  | —                                                        |
| claude-md-management 1.0.0 | ✅   | CLAUDE.md 维护            | 早期因「防覆盖」禁用，现已启用                           |
| chrome-devtools-mcp 1.6.0  | ❌   | Chrome DevTools           | 默认关；需要时中断请用户开 Plugin，禁止自动 merge debug.json |
| context7                   | ✅   | 技术文档                  | Claude **plugin**（不写 MCP）                            |
| firecrawl 1.0.9            | ✅   | 网页抓取                  | Claude **plugin**（不写 MCP）                            |
| github                     | ❌   | GitHub 集成               | plugin=false 且不写 MCP；用 `gh` CLI                     |
| playwright                 | ✅   | 浏览器自动化              | Claude **plugin**；Cursor 优先内置浏览器                 |
| security-guidance 2.0.6    | ❌   | 安全规则                  | 由 `rules/SECURITY.md` 承担                              |
| typescript-lsp 1.0.0       | ❌   | TS LSP                    | 由 serena LSP 能力承担                                   |
| feature-dev                | ❌   | 功能开发                  | 与五阶段流程重叠                                         |
| ralph-loop                 | ❌   | 自动循环                  | 与五阶段冲突                                             |
| claude-hud 0.6.0           | ✅   | 上下文 HUD 状态条         | v11.4.3 起 enabledPlugins=true                           |
| exa 3.4.0                  | ✅   | Exa 搜索                  | Claude **plugin**（不写 MCP；已从 `.mcp.json` 撤出）     |

> 归属：SessionStart→插件 | 守卫/质量门→hooks | 审查→agents。启用的 plugin 里仅 2 个含 hooks（superpowers / claude-mem），零冲突。
> 同名 skill：本地精简版覆盖插件版（token 省 45-74%，中文适配）。

---

## 同步（v11.1 多编辑器 1+N）

| 端                               | 方式                                                                             |
| -------------------------------- | -------------------------------------------------------------------------------- |
| Claude Code                      | 原生读 `~/.claude`，零同步                                                       |
| Cursor：根文件 / skills / agents | 软链接 + Junction（sync.ps1 v20，清单/常量单源 config/sync-manifest.json）       |
| Cursor：rules                    | local plugin 实体 .mdc（唯一规则通道）                                           |
| qoder-cn / trae-cn               | 根文件 6 软链 + `rules/*.mdc` / `user_rules/*.md`（实体+`.claude-managed` 台账） |
| workbuddy                        | 仅 `CLAUDE.md` + `skills/` 联接（SOUL/USER 自有命名空间禁触，跳根索引）          |
| hooks/, commands/, MCP, plugins  | 不同步（TRAE R19 守卫为独立通道：AppData hooks_env 副本）                        |

---

## 变更史

> v11 起版本变更摘要外置 → [CHANGELOG.md](CHANGELOG.md)（v9.0 起全量）。

---

> 版本：13.0.2 | 日期：2026-10-28 | 五柱×阶段主干（`config/workflow.yaml` 单一调度面：阶段门/轨道/完成定义/审查契约/站立 `/goal`；无模型/推理强度）×三横切 | 独立审查必过（两道关；≤3 轮；耗尽 BLOCKED）+ MCP 常驻 5 项 + 图谱三时点 + 工具链 SSOT（pwsh 7.5 / pnpm 11）+ Cursor 完成门不再 followup + 审查只找问题、修改走 change-implementer + L0–L3 + 同步 1+N
