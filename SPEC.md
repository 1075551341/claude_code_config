# SPEC.md — 配置法典索引

> CLAUDE.md 为路由层（≤200行）；本文件为法典索引。
> 版本：10.2 | 五柱×五阶段×三横切 | L0–L3 分级加载 + MCP 分层 + Exa 按需

---

## 架构公式

```
RUNTIME  = Superpowers(方法论) + GSD Redux(上下文) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
FORMAT   = ECC模式(cherry-pick) + anthropics/skills(格式) + best-practice(实证)
REVIEW   = gstack 5审查 + 7补全
OPTIMIZE = RTK(shell token) + caveman(输出token)
INSIGHT  = codegraph(代码图谱MCP) + Exa/Firecrawl(外部调研)  # UA v10 disabled
EXTERNAL = deer-flow 2.0(LangGraph编排,flash/standard/pro/ultra) + task-master(任务管理,core/standard/all)
```

## 三层架构

```
骨架层 (methodology)  → P0 路由集(5) L1×2+L2门控×3 + CORE铁律 + 审查路由 + MCP basic
执行层 (capability)   → 阶段 skill + agent + domain rules（按需 reactive）
护栏层 (guardrails)   → 安全/治理/效率 hook（骨架级4 + 按需级4）
                        + 学习 loop（Stop/PreCompact 触发）
```

## 五阶段处理流程

```
用户输入 → ①规划(/discuss) → ②规格(/plan) → ③执行(/execute) → ④验证(/verify) → ⑤学习(/compact)
              │                  │               │                 │                  │
          HARD-GATE          spec-valid       SDD/TDD组合        gstack审查       pattern提取
          Red Flags表        OpenSpec格式     原子任务(2-5min)    quality-gate    claude-mem SSOT
          一次一问            三轨互斥         两阶段审查         反合理化         上下文压缩
```

---

## 五柱声明

| 柱 | 来源 | 职责 | 骨架 | 执行 | 护栏 |
|----|------|------|------|------|------|
| Superpowers | obra/superpowers | 方法论 + P0 + HARD-GATE | P0×4 | brainstorming→writing-plans(原子)→TDD→verify | def-in-depth + 反合理化 |
| GSD Redux | open-gsd/gsd-core | 上下文工程 + 阈值 (原 gsd-build 已归档) | 三级阈值 + 制品优先 | subagent(两阶段审查) + context-engineering | read-before-edit + canonical-source + trust-but-verify |
| OpenSpec | Fission-AI/OpenSpec | 规格格式 core OPSX | 三轨互斥 | spec-validation + opsx 全链 | spec-reviewer门控 |
| gstack | garrytan/gstack | 审查角色 | 审查路由5+7 + autoplan/ship | eng/ceo/design/qa/security review | browser-qa + quality-gate |
| claude-mem | thedotmack/claude-mem | 跨会话记忆 | SSOT 渐进式披露 | mem-search/timeline/knowledge-agent | MEMORY.md↔claude-mem统一 + Chroma |

---

## 规模约束

| 类型 | v9.1 | 说明 |
|------|------|------|
| 全局 skills | 38 | P0 路由集 5 + supplement 33（含 deep-research/git/pr/mem workflow） |
| 全局 agents | 25 | core 7 + gstack审查 6(+dx) + gstack补全 9 + gstack v0.19=3 |
| 全局 rules | 10 | alwaysApply 1(CORE) + lazy 9（含 OPENSPEC） |
| CLAUDE.md | ≤200 | 精简路由层 + R17-R19 引用 + 五轨搜索策略 + Exa 按需 |
| 全局 hooks | 15 | 核心15（SessionStart 由插件负责）+ _optional 37 |
| 全局 MCP | 5 常驻 | codegraph+crawl+git+fs+time；ops 见 mcp-configs/ |
| 全局 plugins | 18 | 安装18 / 启用15 / 禁用3 |
| 可选外部 | 2 | deer-flow 2.0 + task-master MCP

---

## P0 路由集（5）= L1×2 + L2 门控×3

| Skill | 等级 | 触发 | 阶段 |
|-------|------|------|------|
| using-superpowers | L1 常驻 | 会话开始、分类路由 | 全阶段 |
| change-impact-analysis | L1 按需全文 | 任何修改意图 | 全阶段 |
| brainstorming | L2 门控 | 非简单 ①规划 | ① |
| verification-before-completion | L2 门控 | ④验收 | ④ |
| systematic-debugging | L2 门控 | Bug/测试失败 | ③调试 |

**Cursor**：L2/L3 supplement 用 `disable-model-invocation: true` + 显式 Read。  
**Claude Code**：`layer: skeleton/supplement` + using-superpowers 路由 Read。

### 加载等级 L0–L4（MANIFEST SSOT）

| 等级 | 内容 |
|------|------|
| L0 | CLAUDE-ROUTER + CLAUDE + CORE |
| L1 | using-superpowers, change-impact-analysis |
| L2 | 阶段门控：brainstorming, writing-plans, spec-validation, executing-plans, subagent-driven, verification, debugging |
| L3 | deep-research, adr, workstream, deer-flow, git/pr/mem workflow, … |
| L4 | agents(Task), MCP, claude-mem, lazy rules |

## Workflow Skills

**Superpowers 13**：using-superpowers, brainstorming, writing-plans(原子), executing-plans, verification-before-completion, systematic-debugging, test-driven-development, subagent-driven-development(两阶段审查), using-git-worktrees, receiving-code-review, requesting-code-review, finishing-a-development-branch, writing-skills

**扩展 7**：office-hours, autoplan, browser-qa, design-pipeline, ship, context-engineering, structured-artifacts

**Meta 5**：memory-compression, spec-validation, karpathy-guidelines, caveman-compress, change-impact-analysis

**Mattpocock 2**：triage, improve-codebase-architecture

**项目洞察 1**：understand-anything

---

## 执行层：SDD + TDD 组合

```
模式一 SDD: spec → writing-plans(原子) → subagent(两阶段审查) → verify
模式二 TDD: RED(失败测试) → GREEN(最小通过) → REFACTOR → verify
模式三 组合: writing-plans → 每个task: RED→GREEN→REFACTOR → 两阶段审查 → verify
```

---

## 核心 Agents (7)

| Agent | 阶段 |
|-------|------|
| planner | ①规划 |
| code-reviewer | ④验证 |
| build-error-resolver | ③执行 |
| architect | ①规划 |
| spec-reviewer | ②规格 |
| agentic-orchestrator | ③执行 |
| code-explorer | ③执行 |

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
└─ stop-quality-gate → /verify或/ship时

学习loop (Stop/PreCompact)
├─ pre-compact-state → 压缩前快照 → ~/.claude/state.json
├─ stop-context-monitor → GateGuard（loop/scope/cost）
├─ stop-session-summary → 会话摘要
├─ stop-readme-updater → README更新
├─ post-codegraph-sync → 编辑后增量 codegraph sync
└─ instinct-learning v2 [skill，非hook] → pattern提取（PreCompact/Stop触发调用）
```

---

## 规格三轨（互斥）

| 轨道 | 路径 | 场景 | 入口 |
|------|------|------|------|
| OpenSpec /opsx: | `openspec/changes/<id>/` | 功能变更/brownfield | /opsx:propose → verify → sync → archive |
| GSD Redux | `.planning/phases/` | 大功能多阶段 | /plan |
| 轻量 | `spec/<project>/` | ≤3文件小功能 | /plan |

---

## ECC cherry-pick（v10，无插件）

| 吸收 | 位置 |
|------|------|
| module_resolver.conflicts | MANIFEST.yaml |
| LOCAL_HOOK_PROFILE | hooks/README.md |
| GateGuard 概念 | stop-context-monitor, pre-suggest-compact |

**禁止**安装 everything-claude-code 插件（duplicate hooks）。

---

## MCP 分组（v10.0）

| 分组 | 服务器 | 加载 |
|------|--------|------|
| always | codegraph, crawl, git, fs, time | `.mcp.json` 常驻 |
| ops | redis, sqlite, docker, postgres | `mcp-configs/ops.json` 按需 merge |
| optional-dev | chrome-devtools, figma | `mcp-configs/optional-dev.json` 按需 |

Cursor 侧 → [docs/CURSOR_MCP_PROFILE.md](docs/CURSOR_MCP_PROFILE.md) | 运行时 → [docs/RUNTIME_PLAYBOOK.md](docs/RUNTIME_PLAYBOOK.md)

权威 → `.mcp.json` | 分组 → `mcp/servers.json`

---

## 防互博速查

| 场景 | Owner | 禁止 |
|------|-------|------|
| 计划 | skill/writing-plans | hook/pre-task-planner, agent/agentic-orchestrator |
| 审查 | requesting/receiving-code-review | 独立 code-review skill |
| 记忆 | plugin/claude-mem | agent/context-manager |
| Shell token | hook/pre-rtk-rewrite | skill 重复压缩 |
| 输出 token | skill/caveman-compress | RTK 压缩 agent 文本 |
| 功能 spec | openspec/changes/ | .planning 同功能重写 |
| 测试覆盖 | agent/eng-reviewer | agent/qa (QA 只管边界/回归) |
| pattern提取 | skill/instinct-learning v2 | hook/stop-pattern-extraction (v1已停用) |

---

## 29 仓库完整映射（+plugins-official = 29 编号项，含 19b 子项）

### 五柱 (5)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 1 | obra/superpowers | 14技能+HARD-GATE+Red Flags+原子任务+两阶段审查 | skills/×13, hooks/ |
| 2 | open-gsd/gsd-core | 三级阈值+read-before-edit+canonical-source+trust-but-verify+连续执行 (原 gsd-build/get-shit-done 已归档) | rules/CONTEXT, rules/WORKFLOW |
| 3 | Fission-AI/OpenSpec | proposal→spec→tasks+brownfield+archive | templates/openspec/, spec-validation, commands/propose+apply+archive |
| 4 | garrytan/gstack | 5审查+7补全+浏览器QA+autoplan/ship | agents/×12 |
| 5 | thedotmack/claude-mem | 渐进式披露+向量搜索+6hook SSOT+15技能 | plugin/claude-mem |

### 结构格式 (6)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 6 | affaan-m/ECC | MANIFEST+agent路由+instinct-learning v2 | MANIFEST.yaml, agent.yaml, catalog/ |
| 7 | anthropics/skills | SKILL.md格式标准+跨平台 | skills/*/SKILL.md |
| 8 | shanraisshan/best-practice | 15类别200+行 | rules/BESTPRACTICE |
| 9 | forrestchang/karpathy | 四原则+实施规则+量化测试+弱命令转换表 | rules/CORE, karpathy-guidelines |
| 10 | mattpocock/skills | triage(状态机+P0-P3)+架构改进(8术语+删除测试+Grill) | skills/triage, improve-codebase-architecture |
| 11 | VoltAgent/awesome-design-md | 9章节结构+73品牌+零依赖 | rules/DESIGN, templates/DESIGN.md |

### 优化工具 (4)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 12 | rtk-ai/rtk | Rust CLI 60-90%压缩+100+命令预置 | hooks/pre-rtk-rewrite |
| 13 | JuliusBrussee/caveman | 四级压缩+仅压输出 | skill/caveman-compress |
| 14 | github/github-mcp-server | 80+工具+17工具集 | .mcp.json (gh) |
| 15 | anthropics/claude-code-action | 4后端CI+结构化JSON | templates/github-actions/ |

### 编排增强 (4)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 16 | eyaltoledano/task-master | PRD→结构任务+3级工具裁剪(core/standard/all)+~70% token减少 | 按需MCP |
| 17 | nextlevelbuilder/ui-ux-pro-max | 67风格+161色板+99UX | catalog/skills/ui-ux-pro-max/ |
| 18 | zilliztech/claude-context | Milvus+BM25+按需启用 | .mcp.json optional |
| 19 | bytedance/deer-flow | LangGraph编排+9层Middleware+Sandbox+claude-to-deerflow bridge | WORKFLOW.md + skill 指针 |
| 19b | ruvnet/ruflo | 蜂群拓扑+HNSW向量记忆+SONA自学习（仅概念参考） | WORKFLOW.md 概念 |

### 参考索引 (5)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 20 | ComposioHQ/awesome-claude-skills | 1000+技能索引+渐进式加载 | catalog/ 索引 |
| 21 | hesreallyhim/awesome-claude-code | 配置范式+工具发现 | 外链索引 |
| 22 | x1xhlol/system-prompts | 30+提示词比较+实证分析 | BESTPRACTICE 系统提示词实证段 |
| 23 | Chalarangelo/30-seconds-of-code | 信息架构参考（不直接引入） | catalog 参考 |
| 24 | ruvnet/ruflo | 制品持久化模式（蜂群拓扑/HNSW排除） | WORKFLOW.md |

### 安全 (3)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 25 | trailofbits/claude-code-config | /sandbox+deny+三层防御 | SECURITY.md §11 |
| 26 | marc-shade/claude-code-security | 渐进硬化checklist | SECURITY.md §14 |

### 项目洞察 (2)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 27 | colbymchenry/codegraph | 预索引知识图谱MCP，官方均值 ~16%成本/~47%token/~58%工具调用/~22%更快；MCP默认4工具(F1) | .mcp.json (optional), rules/CONTEXT.md |
| 28 | Lum1104/Understand-Anything | 交互式知识图+引导导览+多Agent管线（l3_on_demand：插件 disabled + catalog 保留） | skill/understand-anything |

### 插件分发 (1)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 29 | anthropics/claude-plugins-official | 官方市场分发 SSOT；gitCommitSha pinning；LSP 族按需 | plugins/installed_plugins.json, settings.json |

---

## Plugins（18 安装 / 15 启用 / 3 禁用）

| Plugin | 状态 | 提供 | 禁用原因 |
|--------|------|------|----------|
| superpowers 6.0.0（目标） | 🟡 | SessionStart + 技能（单 task-reviewer；brainstorming #1773 本地守卫已落地） | 插件当前装 5.1.0，待 Claude Code `/plugin update superpowers@claude-plugins-official` |
| claude-mem 13.6.1 | ✅ | 6hooks + 15技能 | — |
| understand-anything 2.7.5 | ❌ | — | l3_on_demand：插件 disabled + catalog 保留，仅 /understand-* 触发 |
| chrome-devtools-mcp 1.1.1 | ✅ | Chrome DevTools | — |
| frontend-design | ✅ | 前端设计 | — |
| code-review | ✅ | 审查技能(与eng-reviewer互补) | — |
| commit-commands | ✅ | Git快捷 | — |
| context7 | ✅ | 技术文档 | — |
| feature-dev | ✅ | 功能开发 | — |
| firecrawl 1.0.9 | ✅ | 网页抓取 | — |
| github | ✅ | GitHub集成 | — |
| playwright | ✅ | 浏览器自动化 | — |
| security-guidance 2.0.3 | ✅ | 安全规则 | — |
| skill-creator | ✅ | 技能创建 | — |
| typescript-lsp 1.0.0 | ✅ | TS LSP | — |
| ralph-loop | ❌ | 自动循环 | 与五阶段冲突 |
| claude-code-setup | ❌ | 安装向导 | 已配置 |
| claude-md-management | ❌ | 自动改CLAUDE.md | 防覆盖 |

> 归属：SessionStart→插件 | 守卫/质量门→hooks | 审查→agents。15启用中仅2含hooks(superpowers/claude-mem)，零冲突。
> 同名skill：本地精简版覆盖插件版(token省45-74%，中文适配)。

---

## 同步

| 同步 | 方式 |
|------|------|
| CLAUDE.md, skills/, agents/, rules/ | 软链接 (sync.ps1 / sync.sh) |
| hooks/, commands/, MCP, plugins | 不同步 |

---

## v10.2.1 变更摘要（2026-06-19 双源刷新）

- **28 repo 卡片**：+`anthropics-claude-plugins-official`（插件分发 SSOT；27→28）
- **superpowers**：本地 override 已落地（#1773 守卫 + 单 task-reviewer 对齐）；插件二进制 5.1.0 → **6.0.0** 待 Claude Code `/plugin update`（Cursor 无法下载）
- **codegraph**：F1（MCP 默认 4 工具，`codegraph_impact` 需 `CODEGRAPH_MCP_TOOLS`）+ F2（官方四元组 ~16%成本/~47%token/~58%工具调用/~22%更快；47% 为官方数字，仅补全）
- **gsd-core**：v1.5.0 stable 走 ADR 评估（暂锁 1.4.5）
- **UA**：统一 l3_on_demand（删除 disabled 残留）
- **探索链**：codegraph → Grep → Read（impact 优先 explore blast-radius）

## v10.1 变更摘要

- **27 repo 卡片**：`docs/research/repos/{slug}.md`
- **GSD 版本**：open-gsd/gsd-core **1.4.1**（MANIFEST 对齐）
- **探索链**：codegraph → Grep → Read
- **加载**：L0 四入口 + P0 五技能 L1；sync 索引模式
- **调研 SSOT**：30-repo-deep-research-v10.md（v10.1 内容）+ repos/

## v10.0 变更摘要

- **MANIFEST v10**：ecc_integration cherry_pick、module_resolver、thresholds 双轨、ruflo reference_only
- **OpenSpec CLI** 1.4.1 **core**（含 sync）；本地 commands 权威；`openspec init --tools cursor`
- **codegraph mandate**：V16 校验 + `codegraph index`；UA **disabled**
- **调研 SSOT**：仅 `docs/research/30-repo-deep-research-v10.md`（v7/v8 → archive/）
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
- 详图：`spec/claude-config-integration/plan-v9.1-token-loading.md`

## v9.0 变更摘要

- R17-R18：codegraph 探索优先 + claude-mem 记忆优先
- 新增：workstream-management / adr-management / onboarding-guide skills
- 新增：dx-reviewer agent + rules/OPENSPEC.md
- Hook 增强：GateGuard(stop-context-monitor) + codegraph 增量同步 + PreCompact 状态持久化
- P3：taste-memory / claude-to-deerflow skills + workstreams ADR-002
- 文档：`docs/REPO_ANALYSIS.md` | `spec/claude-config-integration/design-v9.md`

---

> 版本：10.2.1 | 日期：2026-06-19 | 五柱×五阶段×三横切 | MCP 分层 + L0–L3
