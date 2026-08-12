# SPEC.md — 配置法典索引

> CLAUDE.md 为路由层（≤200行）；本文件为法典索引。
> 版本：10.17.0 | 五柱×五阶段×三横切 | L0–L3 分级加载 + MCP 9 项三层架构 + TDD/SDD 显式触发 + 问题指纹追踪 + 验证追踪覆盖 MCP 写工具 | UA removed | cbm 已禁用（全盘索引爆 CPU/内存）

---

## 架构公式

```
RUNTIME  = Superpowers(方法论) + GSD Redux(上下文) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
FORMAT   = ECC模式(cherry-pick) + anthropics/skills(格式) + best-practice(实证)
REVIEW   = gstack 5审查 + 7补全
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


| 柱           | 来源                    | 职责                           | 骨架                      | 执行                                                        | 护栏                                                     |
| ----------- | --------------------- | ---------------------------- | ----------------------- | --------------------------------------------------------- | ------------------------------------------------------ |
| Superpowers | obra/superpowers      | 方法论 + P0 + HARD-GATE         | P0×6                    | brainstorming→writing-plans(原子)→execute→verify（TDD 仅显式触发） | def-in-depth + 反合理化                                    |
| GSD Redux   | open-gsd/gsd-core     | 上下文工程 + 阈值 (原 gsd-build 已归档) | 三级阈值 + 制品优先             | context-engineering（subagent 两阶段审查仅显式触发）                  | read-before-edit + canonical-source + trust-but-verify |
| OpenSpec    | Fission-AI/OpenSpec   | 规格格式 core OPSX               | 三轨互斥                    | spec-validation + opsx 全链                                 | spec-reviewer门控                                        |
| gstack      | garrytan/gstack       | 审查角色                         | 审查路由5+7 + autoplan/ship | eng/ceo/design/qa/security review                         | browser-qa + quality-gate                              |
| claude-mem  | thedotmack/claude-mem | 跨会话记忆                        | SSOT 渐进式披露              | mem-search/timeline/knowledge-agent                       | MEMORY.md↔claude-mem统一 + Chroma                        |


---



## 规模约束


| 类型         | v9.1 | 说明                                                                   |
| ---------- | ---- | -------------------------------------------------------------------- |
| 全局 skills  | 45   | P0 路由集 6 + supplement 39（含 deep-research/git/pr/mem workflow）        |
| 全局 agents  | 25   | core 7 + 审查 6 + 补全 6 + v0.19 扩展 4 + 跨模型 1 + doc-writer 1             |
| 全局 rules   | 12   | alwaysApply 1(CORE) + model_decision 10 + glob 1（FRONTEND；不含 README） |
| CLAUDE.md  | ≤200 | 精简路由层 + R17-R19 引用 + 五轨搜索策略 + Exa 按需                                 |
| 全局 hooks   | 20   | 顶层 `.py` 20（经 `_editor_hook_launcher` 分发；含 SessionStart bootstrap）   |
| 全局 MCP     | 9 常驻 | 本地代码4+远端探索2+Web&文档3；debug/fsaccess/ops 见 mcp-configs/                |
| 全局 plugins | 18   | installed_plugins 18；settings enabledPlugins 启用16 / 禁用3              |
| 可选外部       | 2    | deer-flow 2.0 + task-master MCP                                      |


---



## P0 路由集（6）= L1×4 + L2 门控×2


| Skill                          | 等级      | 触发              | 阶段  |
| ------------------------------ | ------- | --------------- | --- |
| using-superpowers              | L1 常驻   | 会话开始、分类路由       | 全阶段 |
| task-triage                    | L1 常驻   | 新任务两大类+关联需改≤2判定 | 全阶段 |
| change-impact-analysis         | L1 按需全文 | 任何修改意图          | 全阶段 |
| brainstorming                  | L1 常驻   | 非简单 ①规划         | ①   |
| verification-before-completion | L2 门控   | ④验收             | ④   |
| systematic-debugging           | L2 门控   | Bug/测试失败        | ③调试 |


**Cursor**：L2/L3 supplement 用 `disable-model-invocation: true` + 显式 Read。
**Claude Code**：`layer: skeleton/supplement` + using-superpowers 路由 Read。

### 加载等级 L0–L4（MANIFEST SSOT；ROUTER 口径等价 L0–L3，L4=L3 子集）


| 等级  | 内容                                                                                             |
| --- | ---------------------------------------------------------------------------------------------- |
| L0  | CLAUDE-ROUTER + CLAUDE + CORE                                                                  |
| L1  | using-superpowers, task-triage, change-impact-analysis, brainstorming                          |
| L2  | 阶段门控：writing-plans, spec-validation, executing-plans, subagent-driven, verification, debugging |
| L3  | deep-research, adr, workstream, deer-flow, git/pr/mem workflow, …                              |
| L4  | agents(Task), MCP, claude-mem, lazy rules（CLAUDE 细分；ROUTER 并入 L3）                              |




## Workflow Skills

**Superpowers 13**：using-superpowers, brainstorming, writing-plans(原子), executing-plans, verification-before-completion, systematic-debugging, test-driven-development, subagent-driven-development(两阶段审查), using-git-worktrees, receiving-code-review, requesting-code-review, finishing-a-development-branch, writing-skills

**扩展 7**：office-hours, autoplan, browser-qa, design-pipeline, ship, context-engineering, structured-artifacts

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
| -------------------- | --- |
| planner              | ①规划 |
| code-reviewer        | ④验证 |
| build-error-resolver | ③执行 |
| architect            | ①规划 |
| spec-reviewer        | ②规格 |
| agentic-orchestrator | ③执行 |
| code-explorer        | ③执行 |




## gstack 审查 5+7

**审查 (skeleton)**：eng-reviewer, ceo-reviewer, designer, dx-reviewer, qa, security-reviewer
**补全 (supplement)**：cso, sre, release-engineer, product-manager, design-engineer, performance-engineer, doc-writer, design-shotgun, pair-agent, land-and-deploy

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
├─ post-codegraph-sync → 编辑后增量 codegraph（debounce；cbm 默认关，仅 KG_SYNC_CBM=1）
├─ stop-knowledge-graph-sync → Stop 强制刷新 codegraph（cbm 同默认禁用）
└─ instinct-learning v2 [skill，非hook] → pattern提取（PreCompact/Stop触发调用）
```

---



## 规格三轨（互斥）


| 轨道              | 路径                       | 场景                          | 入口                                      |
| --------------- | ------------------------ | --------------------------- | --------------------------------------- |
| OpenSpec /opsx: | `openspec/changes/<id>/` | 功能变更/brownfield             | /opsx:propose → verify → sync → archive |
| GSD Redux       | `.planning/phases/`      | 大功能多阶段                      | /plan                                   |
| 轻量              | `spec/<project>/`        | 简单(task-triage判定=关联需改≤2)小功能 | /plan                                   |


---



## ECC cherry-pick（v10，无插件）


| 吸收                        | 位置                                        |
| ------------------------- | ----------------------------------------- |
| module_resolver.conflicts | MANIFEST.yaml                             |
| LOCAL_HOOK_PROFILE        | hooks/README.md                           |
| GateGuard 概念              | stop-context-monitor, pre-suggest-compact |


**禁止**安装 everything-claude-code 插件（duplicate hooks）。

---



## MCP 分组（v10.17，常驻 9）


| 分组       | 服务器                                                  | 加载                                   |
| -------- | ---------------------------------------------------- | ------------------------------------ |
| 本地代码     | codegraph, code-review-graph, aider-repo-map, serena | `.mcp.json` 常驻                       |
| 远端探索     | github, grep                                         | `.mcp.json` 常驻                       |
| Web & 文档 | exa, context7, firecrawl                             | `.mcp.json` 常驻                       |
| debug    | chrome-devtools                                      | `mcp-configs/debug.json` 按需 merge    |
| fsaccess | fs                                                   | `mcp-configs/fsaccess.json` 按需 merge |
| ops      | redis, sqlite, docker, postgres                      | `mcp-configs/ops.json` 按需 merge      |
| collab   | figma, linear, notion, slack                         | `mcp-configs/collab.json`（声明）        |


本地代码四工具分工（codegraph 探索主位 / aider-repo-map 结构概览兼降级 / serena 符号级编辑 / code-review-graph 变更后审查）→ [rules/MCP.md](rules/MCP.md) §4

Cursor 侧 → [docs/CURSOR_MCP_PROFILE.md](docs/CURSOR_MCP_PROFILE.md) | 运行时 → [docs/RUNTIME_PLAYBOOK.md](docs/RUNTIME_PLAYBOOK.md)

权威 → `.mcp.json` | 分组 → `mcp/servers.json`

---



## 防互博速查


| 场景          | Owner                            | 禁止                                                |
| ----------- | -------------------------------- | ------------------------------------------------- |
| 计划          | skill/writing-plans              | hook/pre-task-planner, agent/agentic-orchestrator |
| 审查          | requesting/receiving-code-review | 独立 code-review skill                              |
| 记忆          | plugin/claude-mem                | agent/context-manager                             |
| Shell token | hook/pre-rtk-rewrite             | skill 重复压缩                                        |
| 输出 token    | skill/caveman-compress           | RTK 压缩 agent 文本                                   |
| 功能 spec     | openspec/changes/                | .planning 同功能重写                                   |
| 测试覆盖        | agent/eng-reviewer               | agent/qa (QA 只管边界/回归)                             |
| pattern提取   | skill/instinct-learning v2       | hook/stop-pattern-extraction (v1已停用)              |


---



## 29 仓库完整映射（+plugins-official = 29 编号项，含 19b 子项）



### 五柱 (5)


| #   | 仓库                    | 吸收                                                                                           | 落地                                                                   |
| --- | --------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1   | obra/superpowers      | 14技能+HARD-GATE+Red Flags+原子任务+两阶段审查                                                          | skills/×13, hooks/                                                   |
| 2   | open-gsd/gsd-core     | 三级阈值+read-before-edit+canonical-source+trust-but-verify+连续执行 (原 gsd-build/get-shit-done 已归档) | rules/CONTEXT, rules/WORKFLOW                                        |
| 3   | Fission-AI/OpenSpec   | proposal→spec→tasks+brownfield+archive                                                       | templates/openspec/, spec-validation, commands/propose+apply+archive |
| 4   | garrytan/gstack       | 5审查+7补全+浏览器QA+autoplan/ship                                                                  | agents/×12                                                           |
| 5   | thedotmack/claude-mem | 渐进式披露+向量搜索+6hook SSOT+15技能                                                                   | plugin/claude-mem                                                    |




### 结构格式 (6)


| #   | 仓库                          | 吸收                                     | 落地                                           |
| --- | --------------------------- | -------------------------------------- | -------------------------------------------- |
| 6   | affaan-m/ECC                | MANIFEST+agent路由+instinct-learning v2  | MANIFEST.yaml, agent.yaml, catalog/          |
| 7   | anthropics/skills           | SKILL.md格式标准+跨平台                       | skills//SKILL.md                             |
| 8   | shanraisshan/best-practice  | 15类别200+行                              | rules/BESTPRACTICE                           |
| 9   | forrestchang/karpathy       | 四原则+实施规则+量化测试+弱命令转换表                   | rules/CORE, karpathy-guidelines              |
| 10  | mattpocock/skills           | triage(状态机+P0-P3)+架构改进(8术语+删除测试+Grill) | skills/triage, improve-codebase-architecture |
| 11  | VoltAgent/awesome-design-md | 9章节结构+73品牌+零依赖                         | rules/DESIGN, templates/DESIGN.md            |




### 优化工具 (4)


| #   | 仓库                            | 吸收                         | 落地                        |
| --- | ----------------------------- | -------------------------- | ------------------------- |
| 12  | rtk-ai/rtk                    | Rust CLI 60-90%压缩+100+命令预置 | hooks/pre-rtk-rewrite     |
| 13  | JuliusBrussee/caveman         | 四级压缩+仅压输出                  | skill/caveman-compress    |
| 14  | github/github-mcp-server      | 80+工具+17工具集                | .mcp.json (gh)            |
| 15  | anthropics/claude-code-action | 4后端CI+结构化JSON              | templates/github-actions/ |




### 编排增强 (4)


| #   | 仓库                             | 吸收                                                         | 落地                            |
| --- | ------------------------------ | ---------------------------------------------------------- | ----------------------------- |
| 16  | eyaltoledano/task-master       | PRD→结构任务+3级工具裁剪(core/standard/all)+~70% token减少            | 按需MCP                         |
| 17  | nextlevelbuilder/ui-ux-pro-max | 67风格+161色板+99UX                                            | catalog/skills/ui-ux-pro-max/ |
| 29  | DeusData/codebase-memory-mcp   | 知识图谱 L4 架构/ADR/变更                                          | optional-dev.json             |
| 18  | zilliztech/claude-context      | archived_redirect → cbm                                    | 仅历史卡                          |
| 19  | bytedance/deer-flow            | LangGraph编排+9层Middleware+Sandbox+claude-to-deerflow bridge | WORKFLOW.md + skill 指针        |
| 19b | ruvnet/ruflo                   | 蜂群拓扑+HNSW向量记忆+SONA自学习（仅概念参考）                               | WORKFLOW.md 概念                |




### 参考索引 (5)


| #   | 仓库                               | 吸收                   | 落地                    |
| --- | -------------------------------- | -------------------- | --------------------- |
| 20  | ComposioHQ/awesome-claude-skills | 1000+技能索引+渐进式加载      | catalog/ 索引           |
| 21  | hesreallyhim/awesome-claude-code | 配置范式+工具发现            | 外链索引                  |
| 22  | x1xhlol/system-prompts           | 30+提示词比较+实证分析        | BESTPRACTICE 系统提示词实证段 |
| 23  | Chalarangelo/30-seconds-of-code  | 信息架构参考（不直接引入）        | catalog 参考            |
| 24  | ruvnet/ruflo                     | 制品持久化模式（蜂群拓扑/HNSW排除） | WORKFLOW.md           |




### 安全 (3)


| #   | 仓库                              | 吸收                 | 落地              |
| --- | ------------------------------- | ------------------ | --------------- |
| 25  | trailofbits/claude-code-config  | /sandbox+deny+三层防御 | SECURITY.md §11 |
| 26  | marc-shade/claude-code-security | 渐进硬化checklist      | SECURITY.md §14 |




### 项目洞察 (1)


| #   | 仓库                     | 吸收                                                            | 落地                                     |
| --- | ---------------------- | ------------------------------------------------------------- | -------------------------------------- |
| 27  | colbymchenry/codegraph | 预索引知识图谱MCP，官方均值 ~16%成本/~47%token/~58%工具调用/~22%更快；MCP默认4工具(F1) | .mcp.json (optional), rules/CONTEXT.md |




### 插件分发 (1)


| #   | 仓库                                 | 吸收                                       | 落地                                            |
| --- | ---------------------------------- | ---------------------------------------- | --------------------------------------------- |
| 29  | anthropics/claude-plugins-official | 官方市场分发 SSOT；gitCommitSha pinning；LSP 族按需 | plugins/installed_plugins.json, settings.json |


---



## Plugins（18 安装 / 7 启用 / 9 禁用 / 2 未在 settings 声明）

> v10.17 按 `plugins/installed_plugins.json` × `settings.json.enabledPlugins` 实测重写。
> 此前本表长期停留在旧快照（声称 15 启用），与运行态严重不符。


| Plugin                     | 状态  | 提供                   | 说明                                            |
| -------------------------- | --- | -------------------- | --------------------------------------------- |
| superpowers 6.2.0          | ✅   | SessionStart + 方法论技能 | 五柱之一，随上游自动更新                                  |
| claude-mem 13.13.1         | ✅   | 6 hooks + 记忆技能       | 五柱之一（R18 记忆优先）                                |
| code-review                | ✅   | 审查技能                 | 与 eng-reviewer 互补                             |
| commit-commands            | ✅   | Git 快捷命令             | —                                             |
| frontend-design            | ✅   | 前端设计                 | —                                             |
| skill-creator              | ✅   | 技能创建                 | —                                             |
| claude-md-management 1.0.0 | ✅   | CLAUDE.md 维护         | 早期因「防覆盖」禁用，现已启用                               |
| chrome-devtools-mcp 1.6.0  | ❌   | Chrome DevTools      | v10.17 浏览器按需化；需要时走 `mcp-configs/debug.json`   |
| context7                   | ❌   | 技术文档                 | 能力由 `.mcp.json` 的 context7 MCP 承担，避免同端双挂      |
| firecrawl 1.0.9            | ❌   | 网页抓取                 | 同上，走 MCP                                      |
| github                     | ❌   | GitHub 集成            | 同上，走 MCP                                      |
| playwright                 | ❌   | 浏览器自动化               | Cursor 优先内置 `cursor-ide-browser`              |
| security-guidance 2.0.6    | ❌   | 安全规则                 | 由 `rules/SECURITY.md` 承担                      |
| typescript-lsp 1.0.0       | ❌   | TS LSP               | 由 serena LSP 能力承担                             |
| feature-dev                | ❌   | 功能开发                 | 与五阶段流程重叠                                      |
| ralph-loop                 | ❌   | 自动循环                 | 与五阶段冲突                                        |
| claude-hud 0.6.0           | ➖   | 上下文 HUD 状态条          | 未在 enabledPlugins 声明（默认行为）                    |
| exa 3.4.0                  | ➖   | Exa 搜索               | 未在 enabledPlugins 声明；Claude 侧走 MCP，Cursor 走插件 |


> 归属：SessionStart→插件 | 守卫/质量门→hooks | 审查→agents。启用的 7 个里仅 2 个含 hooks（superpowers / claude-mem），零冲突。
> 同名 skill：本地精简版覆盖插件版（token 省 45-74%，中文适配）。

---



## 同步


| 同步                                  | 方式                       |
| ----------------------------------- | ------------------------ |
| CLAUDE.md, skills/, agents/, rules/ | 软链接 (sync.ps1 / sync.sh) |
| hooks/, commands/, MCP, plugins     | 不同步                      |


---



## v10.17.0 变更摘要（2026-08-12）

配置精简去重 + 执行层硬化。三个长期症状（同问题重复处理 / 关联文件遗漏 / 改完影响其他功能）此前只有文字提示、没有机械拦截，本版把它们逐条落到 hook 上。

- **MCP 收敛 9 项三层**：本地代码（codegraph / code-review-graph / aider-repo-map / serena）+ 远端探索（github / grep）+ Web 文档（exa / context7 / firecrawl）。`chrome-devtools`、`fs` 从常驻降级为按需 profile（`mcp-configs/debug.json`、`mcp-configs/fsaccess.json`）——`fs` 全盘可写正是绕过验证追踪的通道之一。codegraph 1.5.0 / firecrawl 3.23.9 / exa 3.4.0 补版本钉扎（R14）。新增本地代码四工具分工表（`rules/MCP.md`、`docs/TOOL_MATCHING_GUIDE.md`）
- **判定逻辑单源化**：SSOT 唯一在 `skills/task-triage/SKILL.md`；下游（CLAUDE-ROUTER / skills-INDEX / RUNTIME_PLAYBOOK / using-superpowers）要么写全六条判定条件，要么只写指针，消除「两条缩写」漂移；非简单路径补回被整条跳过的 grill；五阶段图改 TDD/SDD 显式触发
- **C1 重复处理**：指纹算法与状态双端共用 `hooks/_lib/issue_state.py`，单一状态文件 `~/.claude/.state/issue-tracker.json`（此前 Claude 与 Cursor 各写各的，跨编辑器互不可见）；`stop-verification-gate` 验证通过时置 `resolved=true`，激活此前无人写入的轻提示死分支
- **C2 遗漏**：影响门从「每会话一次」改为「每文件首次编辑」双端注入；Stop 门新增 `git status --porcelain` 与 `edited_files` 交叉核查，堵住 MCP / Bash 重定向写入的绕过通道
- **C3 回归**：`settings.json` 与 Cursor `hooks.json` 的 matcher 补 `mcp__serena__.`* / `mcp__fs__.*`（必须带 `.*`，裸名永不触发）；写工具识别与路径解析统一到 `hooks/_lib/tool_paths.py`；Stop 门新增非功能变更的回归测试证据校验
- **同步链修复（sync v18.4）**：`$L0_ROOT_ITEMS` 补齐 SPEC / MANIFEST / 三个 INDEX / agent.yaml / CLAUDE-ROUTER.mdc，并从「仅 Cursor」放开到**除 workbuddy 外的所有编辑器**——总纲链要求 Agent 按编辑器相对路径 Read 这些文件，v18.3 的收窄让 qoder / trae / codearts 断链；集合在 `sync.ps1` / `sync.sh`(v2.3) / `check.ps1` / `impact_sync.SYNC_FILES` 四处统一（`agent.yaml` 此前只在其中两处）。`impact_sync.rules_out_of_sync()` 改查 plugin 路径并比对内容哈希（此前查 `~/.cursor/rules/` 且比 mtime，是每次会话「过期规则」误报的根因，实测规则无漂移）；guard 1.1.9
- **结构整备**：MANIFEST excludes 中的已移除组件加注说明；`deep-research` split-brain 消歧为「skills/ 权威、catalog/ 变体」；新增 `catalog/INDEX.md`（101 skills + 43 agents + 15 rules 一页式清单 + 7 个同名项消歧表）；agent.yaml 补注册 issue-tracker hook 与 `/sync` 命令；`templates/claude-settings/hooks.snippet.json` 让被 gitignore 的 hook 注册可复现；版本串统一 v10.17.0 / sync v18.4
- **仓库瘦身与 .gitignore 归位**：过程制品（`spec/`、`docs/superpowers/plans/`）移出版本库只留本地最近一次；删除 v10.5/v10.5.1 设计、v10.10 计划、`usage-audit-v10.6.md`、`research/archive/` 与 3 个一次性脚本（`migrate-from-legacy.py` 经核查是 catalog 安装工具、被 10 处文档引用，保留）。`.gitignore` 修三处误伤：`.cursor/` 整目录忽略曾吞掉 5 个 opsx 命令与 5 个 openspec 技能、`*.txt` 曾吞掉 8 份 `skills/*/LICENSE.txt` 与 `templates/cursor-user-rules-snippet.txt`、`config.json` 无锚点会命中任意层级
- **SSOT**：`.mcp.json`（MCP）+ `skills/task-triage/SKILL.md`（判定）+ `hooks/_lib/issue_state.py`（重复追踪）+ `hooks/_lib/tool_paths.py`（写工具识别）+ `hooks/_lib/gate_messages.md`（门控文本）+ `config/quality_gates.json`（门控配置）



## v10.15.0 变更摘要（2026-08-12）

- **MCP 11 项三层架构**：github 启用官方远端（Bearer `GITHUB_TOKEN`）；fs 启用全盘符（C:/D:/E:）；exa 补 `EXA_API_KEY`；chrome-devtools 保持 `@latest`（R14 例外，用户决策）；`_comment` 重写如实描述
- **TDD/SDD 显式触发**：`CLAUDE.md` SDD+TDD 行改为「仅用户明确要求时启用」；task-triage / skills-INDEX / SPEC / gate_messages 同步
- **问题指纹追踪（新 hook）**：`pre-userprompt-issue-tracker.py`（UserPromptSubmit，永不阻断）— 同问题重复出现时注入「先查上轮结论禁止重做」；推翻 v10.13「不做计数器」决策；状态 `~/.claude/.state/issue-tracker.json`；Cursor 端 `issue_tracker.py`（guard 1.1.8）
- **验证门补强**：残留引用检测从全量档专属移为任何修改必须（两档同强制）；新增「非功能变更回归保持」核验；疑难项 grill 前置在分类门/影响门文本中醒目标注
- **配置文档一致性**：`.mcp.json` 为唯一事实源；mcp/servers.json、mcp/README.md、docs/TOOL_MATCHING_GUIDE.md、docs/CURSOR_MCP_PROFILE.md、rules/MCP.md、mcp-configs/*、templates/cursor-guard/mcp-recommended.json 全量同步至 v10.15
- **SSOT**：`.mcp.json`（MCP）+ `hooks/pre-userprompt-issue-tracker.py`（重复追踪）+ `hooks/_lib/gate_messages.md`（门控文本）+ `config/quality_gates.json`（issue_tracker 配置节）



## v10.13.0 变更摘要（2026-08-01）

- **Phase0 前置盘点**：分类前强制盘点已知文件/工具/记忆/成功标准；未盘点不得宣称简单
- **持续处理 = 执行升档**：attempt≥2 / 首轮未解决 → verify_tier=全量 **且** 执行升档非简单（不再停留简单旁路）
- **一次改完**：简单路径仅 attempt=1；清单膨胀>2 立即执行升档；禁止多轮简单旁路
- **模型档映射表**：frontier/mid/light 典型模型对照，防虚报；设计 doc → `spec/task-difficulty-precision/design.md`
- **SSOT**：`skills/task-triage`；verification / gate_messages / CLAUDE / ROUTER / using-superpowers 短引用对齐



## v10.12.0 变更摘要（2026-08-01）

- **简单判定放宽计数**：关联需改文件 ≤2（仅 Edit 逻辑源；只读/sync 镜像不计）+ 白名单 + 六维全低 + 模型匹配低
- **六维**：原五维 + ⑥模型匹配（frontier/mid/light 自报，防预期过高/过低）
- **全任务强制验证**：删除「轻量验证」旁路措辞；verify_tier=比例|全量；持续处理同一问题 → 验证升全量
- **分类输出契约**：大类 | 需改列表 | 模型档 | verify_tier | 置信度 | 成功标准
- **SSOT**：`skills/task-triage` + `verification-before-completion`；gate_messages / CLAUDE / ROUTER / using-superpowers 短引用对齐



## v10.11.0 变更摘要（2026-08-01）

- **44 仓库全量调研**：SSOT 30-repo → `44-repo-deep-research-v10.11.md`（四分类：29 已集成 + 15 新卡 + 2 不集成）；COVERAGE 矩阵 44；repos/ 新增 15 张浅层卡（anthropics-claude-code / musistudio-claude-code-router / openai-codex-plugin-cc / VoltAgent-subagents 等）
- **版本对齐运行态（非升级）**：superpowers 6.2.0 / claude-mem 13.12.4 / codegraph MCP 1.5.0（插件 autoUpdater 自动更新，installed_plugins.json 为事实源）；rtk 0.44.1 确认
- **0 新增组件**：45 skills / 25 agents / 5 MCP 常驻 保持；新仓库全部卡片/文档级记录（CCR/codex-plugin-cc/claude-code-best/SuperClaude 评估=不集成，MANIFEST reference concern）
- **agent.yaml 漂移修复**：v9.0 → v10.11.0；p0 补 task-triage（6）；mcp_loading 对齐 .mcp.json 常驻 5；global_skills_max 45
- **清理（保留最全最新一次）**：删 v10.6/v10.7 计划 + diagnostic-v10.5.2 + 7 空 backups 子目录；保留 v10.10 计划 + 44-repo SSOT
- **可选变更（用户确认）**：feature-dev 插件停用（MANIFEST 冲突落地）；codegraph CLI 0.9.7 → 1.5.0（版本分裂消除）；autoCompactWindow 按模型窗口计算=1M 保持不变；fs MCP 未选
- **validate_config warn 收敛**：V17 env 显式化（70/70/90）+ V9 deny 补 3 条 + V1 触发词消歧（9 → 1 warn）



## v10.10.0 变更摘要（2026-07-31）

- **同步链路修复**：sync.ps1 v18.2 新增 `-Scope rules|indexes|all` + `-Force`（对齐 Cursor Guard sync_runner 契约，修复自动同步必失败）；变更检测（hash 跳过）；结尾图谱刷新去 force；Guard hooks.json 移除 postToolUse 双注册；Cursor 规则通道 = local plugin 永久方案（`~/.cursor/rules` 实测不生效，不做其他通道尝试）
- **安全**：settings.json 密钥外置（环境变量）+ gitignore + 取消跟踪；sync-mode.json 删除
- **cbm 永久禁用**：全盘索引爆 CPU/内存（用户确认）；SPEC/MANIFEST/CORE/plugin 模板统一口径，codegraph 全权替代；validate_config V18 改为禁用断言
- **重复合并**：CLAUDE.md -9 行（R17 收敛 CORE SSOT 指针、场景映射表单点化、@RTK.md 指针化、/deer-flow 命令对齐）；版本/计数全串对齐 v10.10.0（skills 45、hooks 16、global_skills_max 45）
- **MCP 分层**：crawl 移 optional-dev.json 按需，常驻 5（codegraph+fetch+git+fs+time）
- **可测量性**：stop-session-summary 追加 skill/agent 真实触发日志（logs/skill-triggers.jsonl），下一轮 usage-audit 数据源



## v10.9.0 变更摘要（2026-07-31）

> ⚠️ 以下 v10.9 判定口径**已废止**（历史记录，勿据此执行）：现行为 **六维** + **关联需改≤2**，见 `skills/task-triage/SKILL.md`。

- **任务分类重构**：两大类（简单/非简单）→ 使用类型细分（文档/实现/配置值/Bug / Bug/功能/架构/配置/删除/调研），`skills/task-triage/SKILL.md` 为唯一 SSOT
- ~~**简单判定严格收窄**：单文件(=1) + 白名单 + 五维全低~~（v10.13 起改为六维 + ≤2，本行仅存档）
- ~~**Bug 归属**：可复现+根因明确+单文件 → 简单~~（现行：关联需改≤2）；其余 → triage(P0-P3)→systematic-debugging
- **双端同步**：gate_messages P0 段/CLAUDE/ROUTER/using-superpowers/MANIFEST/索引三文件/Cursor 插件副本统一 v10.9.0



## v10.7.0 变更摘要（2026-07-30）

- **配置驱动门控**：分类路由/完成验证/变更影响从模型自觉升级为 hook 强制注入（双端）。文本 SSOT `hooks/_lib/gate_messages.md`；Claude Code 新增 SessionStart/UserPromptSubmit 注册 + `pre-userprompt-verify-gate` + `pre-edit-impact-nudge`；Cursor Guard 新增 `verification_gate`/`impact_nudge`，`session_bootstrap` 注入 P0 门
- **变更影响门**：首编辑注入提醒，**永不 deny**（用户决策）；状态 `~/.claude/.state/impact-nudge.json` / Guard state，7 天清理
- **hooks 对齐**：settings.json 注册 7→15（补注册历史遗漏 5：pre-read-before-edit/pre-manifest-validator/pre-compact-state/stop-quality-gate/stop-session-summary，与 README v5.1 文档口径对齐）；Cursor Guard 15→17
- **stdin UTF-8 修复**：Windows cp936 致中文 prompt 乱码，三个新 Claude hook 与 Guard `hook_io.read_stdin` 显式 UTF-8 解码
- **Cursor 全量同步**：`sync.ps1 -All` 12 rules verbatim 部署为 .mdc + skills 44 + agents 25
- **agent.yaml 漂移清理**：mcp_loading 去 figma/puppeteer/glif 对齐 `.mcp.json`；limits 对齐实际（rules 12/skills 44/agents 25）；hooks.core 对齐注册态 15
- 详图：`docs/superpowers/plans/2026-07-30-v10.7-gate-enforcement.md`



## v10.6.0 变更摘要（2026-07-29）

- **版本对齐**：SPEC/README/skills-INDEX/MANIFEST/research-README 版本串统一（修复 10.1/10.4.0/10.5.1 漂移）
- **文档精简**：旧优化 plan（v10.5/v10.5.1）合并为 `docs/superpowers/plans/2026-07-29-v10.6-optimization.md` 后删除原件；`gsd-gaps-v10.md` 删除（已被 v10.5.2 调研吸收）；`REPO_ANALYSIS.md` 并入 `COVERAGE.md` 后删除；`reference/task-master-integration.md` 归档至 `docs/research/archive/`
- **常驻瘦身**：`rules/CORE.md` 316→≤150 行，治理详情迁 `rules/GOVERNANCE.md`（model_decision 触发）；CONTEXT/BESTPRACTICE/WORKFLOW 去除与 CORE 重复段
- **索引补全**：skills-INDEX 补登 7 技能（44 全量）；修复 2 个 SKILL.md 重复 frontmatter
- **hooks 治理**：3 个 stub 移 `_deprecated/`；`_optional/` → `_archive/`（非激活资产库）
- **使用率审计**：`docs/research/usage-audit-v10.6.md`（零触发项降级/废弃候选）
- **OpenSpec**：三处表面职责边界文档化
- 访谈决策记录：见 v10.6 优化计划文档



## v10.5.1 变更摘要（2026-07-17）

- **调研**：分层 delta 刷新 29 卡 + SSOT；上游漂移仅文档「待评估」（R14）
- **cbm**：架构/ADR/变更/跨服务 **场景强制**；未调用 → `DONE_WITH_CONCERNS`；Claude 仍不进常驻 5
- **同步**：`sync.ps1 -All` 修 CONTEXT/CORE/MCP 过期
- 详图：`spec/claude-config-integration/design-v10.5.1.md` + plan（已合并入 `docs/superpowers/plans/2026-07-29-v10.6-optimization.md`）



## v10.5 变更摘要（2026-07-17）

- **探索链**：codegraph → codebase-memory(L4) → Grep → Read
- **Cursor Guard**：`explore.enforce_mode=soft_block`（Grep/Glob）
- **MCP 常驻**：纠偏为 5（chrome-devtools 回 optional-dev）
- **调研**：28 active；上游版本漂移仅文档跟踪（R14）



## v10.2.1 变更摘要（2026-06-19 双源刷新）

- **28 repo 卡片**：+`anthropics-claude-plugins-official`（插件分发 SSOT；27→28）
- **superpowers**：本地 override 已落地（#1773 守卫 + 单 task-reviewer 对齐）；插件二进制 5.1.0 → **6.0.0** 待 Claude Code `/plugin update`（Cursor 无法下载）
- **codegraph**：F1（MCP 默认 4 工具，`codegraph_impact` 需 `CODEGRAPH_MCP_TOOLS`）+ F2（官方四元组 ~16%成本/~47%token/~58%工具调用/~22%更快；47% 为官方数字，仅补全）
- **gsd-core**：v1.5.0 stable 走 ADR 评估（暂锁 1.4.5）
- **探索链**：codegraph → Grep → Read（impact 优先 explore blast-radius）



## v10.1 变更摘要

- **27 repo 卡片**：`docs/research/repos/{slug}.md`
- **GSD 版本**：open-gsd/gsd-core **1.4.1**（MANIFEST 对齐）
- **探索链**：codegraph → Grep → Read
- **加载**：L0 四入口 + P0 五技能 L1；sync 索引模式
- **调研 SSOT**：44-repo-deep-research-v10.11.md（v10.11 内容）+ repos/



## v10.0 变更摘要

- **MANIFEST v10**：ecc_integration cherry_pick、module_resolver、thresholds 双轨、ruflo reference_only
- **OpenSpec CLI** 1.4.1 **core**（含 sync）；本地 commands 权威；`openspec init --tools cursor`
- **codegraph mandate**：V16 校验 + `codegraph index`；UA 当时 **disabled**（v10.5 已 **removed**，见 ADR-2026-07-17）
- **调研 SSOT**：仅 `docs/research/44-repo-deep-research-v10.11.md`（历史多版本已清理）
- **Firecrawl**：`scripts/firecrawl-mcp.ps1` 包装启动
- **Git 禁令**：禁止 Agent auto commit / stash（Guard v1.1.6）
- **阈值**：Cursor/Claude 70/90 + GSD 70% 逻辑断点
- **Claude Code auto-compact SSOT**：`config/model-context-windows.json` + `hooks/_lib/context_thresholds.py`；详 `docs/RUNTIME_PLAYBOOK.md` §上下文治理



## v9.2 变更摘要

- **MCP 分层**：Claude Code `.mcp.json` 常驻 5；ops/optional-dev 迁入 `mcp-configs/`
- **Cursor 文档化**：CURSOR_MCP_PROFILE 反映用户精简后的插件/MCP 清单
- **CORE 去重**：缩短时间 API 示例；工作原则改指针
- **V15 校验**：`validate_config.py` loading_tier + disable-model-invocation
- **RUNTIME_PLAYBOOK**：五阶段 + 调研三档 + 上下文 + R16 单页 SSOT



## v9.1 变更摘要

- **L0–L4 分级加载**：P0 改称「路由集」；L1 混合（using-superpowers + change-impact 常驻）
- **slash-only**：除 L1 外全部 skills 加 `disable-model-invocation`（Cursor token 减负）
- **调研三档**：L1 Context7/Exa → L2 Exa+Firecrawl → L3 deep-research
- **User Rules 迁出**：git-workflow / pr-workflow / claude-mem-maintenance（L3）
- **spec-validation**：仅②门控；④ exclusively verification-before-completion
- **插件边界**：禁用 compound-engineering；审查走 `~/.claude/agents/` gstack
- 详图：`spec/claude-config-integration/design-v10.5.md` + plan（已合并入 `docs/superpowers/plans/2026-07-29-v10.6-optimization.md`）



## v9.0 变更摘要

- R17-R18：codegraph 探索优先 + claude-mem 记忆优先
- 新增：workstream-management / adr-management / onboarding-guide skills
- 新增：dx-reviewer agent + rules/OPENSPEC.md
- Hook 增强：GateGuard(stop-context-monitor) + codegraph 增量同步 + PreCompact 状态持久化
- P3：taste-memory / claude-to-deerflow skills + workstreams ADR-002
- 文档：`docs/REPO_ANALYSIS.md` | `spec/claude-config-integration/design-v9.md`

---

> 版本：10.17.0 | 日期：2026-08-12 | 五柱×五阶段×三横切 | MCP 9 项三层 + L0–L3

