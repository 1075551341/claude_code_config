# SPEC.md — 配置法典索引

> CLAUDE.md 为路由层（≤280行）；本文件为法典索引。
> 版本：7.0 | 五柱×五阶段×三层（骨架/执行/护栏） | 28仓库全量整合

---

## 架构公式

```
RUNTIME  = Superpowers(方法论) + GSD Redux(上下文) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
FORMAT   = ECC(路由) + anthropics/skills(格式) + best-practice(实证)
REVIEW   = gstack 5审查 + 7补全
OPTIMIZE = RTK(shell token) + caveman(输出token)
INSIGHT  = codegraph(代码图谱MCP) + Understand-Anything(交互知识图)
```

## 三层架构

```
骨架层 (methodology)  → P0 skills ×4 + CORE铁律 R1-R13 + 审查路由 + MCP basic
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
| GSD Redux | open-gsd/get-shit-done-redux | 上下文工程 + 阈值 | 三级阈值 + 制品优先 | subagent(两阶段审查) + context-engineering | read-before-edit + canonical-source + trust-but-verify |
| OpenSpec | Fission-AI/OpenSpec | 规格格式 | 三轨互斥 | spec-validation + /propose→/apply→/archive | spec-reviewer门控 |
| gstack | garrytan/gstack | 审查角色 | 审查路由5+7 + autoplan/ship | eng/ceo/design/qa/security review | browser-qa + quality-gate |
| claude-mem | thedotmack/claude-mem | 跨会话记忆 | SSOT 渐进式披露 | mem-search/timeline/knowledge-agent | MEMORY.md↔claude-mem统一 + Chroma |

---

## 规模约束

| 类型 | v7.0 | 说明 |
|------|------|------|
| 全局 skills | 28 | superpowers 13 + 扩展 7 + meta 4 + mattpocock 2 + instinct-learning 1 + understand-anything 1 |
| 全局 agents | 19 | core 7 + gstack审查 5 + gstack补全 7 |
| 全局 rules | 10 | CONTEXT 扩展 codegraph+claude-mem 搜索策略 |
| CLAUDE.md | ≤290 | 精简路由层 + codegraph/understand-anything/plugins 指针 |
| 全局 hooks | 14 | 核心14（SessionStart 由插件负责）+ _optional 37 |
| 全局 MCP | 19 | 基础 18 + codegraph (optional) |
| 全局 plugins | 18 | 安装18 / 启用15 / 禁用3（ralph-loop/claude-code-setup/claude-md-management） |

---

## P0 强制 Skill (4)

| Skill | 触发 | 阶段 | 层 |
|-------|------|------|-----|
| using-superpowers | 会话开始 | 骨架 | 骨架 |
| brainstorming | 方案/架构/非简单任务 | ①规划 | 骨架 |
| verification-before-completion | 完成/验收 | ④验证 | 骨架 |
| systematic-debugging | 调试/bug | ③执行 | 骨架 |

## Workflow Skills

**Superpowers 13**：using-superpowers, brainstorming, writing-plans(原子), executing-plans, verification-before-completion, systematic-debugging, test-driven-development, subagent-driven-development(两阶段审查), using-git-worktrees, receiving-code-review, requesting-code-review, finishing-a-development-branch, writing-skills

**扩展 7**：office-hours, autoplan, browser-qa, design-pipeline, ship, context-engineering, structured-artifacts

**Meta 4**：memory-compression, spec-validation, karpathy-guidelines, caveman-compress

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

**审查 (skeleton)**：eng-reviewer, ceo-reviewer, designer, qa, security-reviewer
**补全 (supplement)**：cso, sre, release-engineer, product-manager, design-engineer, performance-engineer, doc-writer

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
├─ pre-compact-state → 压缩前快照
├─ stop-session-summary → 会话摘要
├─ stop-readme-updater → README更新
└─ instinct-learning v2 [skill，非hook] → pattern提取（PreCompact/Stop触发调用）
```

---

## 规格三轨（互斥）

| 轨道 | 路径 | 场景 | 入口 |
|------|------|------|------|
| OpenSpec /opsx: | `openspec/changes/<id>/` | 功能变更/brownfield | /opsx:propose |
| GSD Redux | `.planning/phases/` | 大功能多阶段 | /plan |
| 轻量 | `spec/<project>/` | ≤3文件小功能 | /plan |

---

## MCP 分组

| 分组 | 服务器 |
|------|--------|
| always | memory, thinking, fs, fetch, time |
| dev | gh(新版80+工具), git, ctx7, pw, crawl, chrome-devtools |
| ops | redis, sqlite, docker, postgres |
| search | brave, exa |
| design | figma |
| optional | postgres, codegraph |

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

## 28 仓库完整映射

### 五柱 (5)
| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 1 | obra/superpowers | 14技能+HARD-GATE+Red Flags+原子任务+两阶段审查 | skills/×13, hooks/ |
| 2 | open-gsd/get-shit-done-redux | 三级阈值+read-before-edit+canonical-source+trust-but-verify+连续执行 | rules/CONTEXT, rules/WORKFLOW |
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
| 16 | eyaltoledano/task-master | PRD→结构任务+3级工具裁剪 | templates/taskmaster/ |
| 17 | nextlevelbuilder/ui-ux-pro-max | 67风格+161色板+99UX (5 CSV已落) | catalog/skills/ui-ux-pro-max/ |
| 18 | zilliztech/claude-context | Milvus+BM25+40% token节省 | .mcp.json optional |
| 19 | bytedance/deer-flow | 渐进式加载+DAG编排 | WORKFLOW.md |

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
| 27 | colbymchenry/codegraph | 预索引知识图谱MCP，~35% token节省，20+语言+14框架+跨语言桥接 | .mcp.json (optional), rules/CONTEXT.md |
| 28 | Lum1104/Understand-Anything | 交互式知识图+引导导览+多Agent管线 | skill/understand-anything, plugin/understand-anything |

---

## 同步

| 同步 | 方式 |
|------|------|
| CLAUDE.md, skills/, agents/, rules/ | 软链接 (sync.ps1) |
| hooks/, commands/, MCP, plugins | 不同步 |

---

_版本：7.0 | 日期：2026-05-28 | 五柱×五阶段×三层(骨架/执行/护栏) | 28仓库全量整合_
