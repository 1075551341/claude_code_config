# SPEC.md — 配置法典索引

> CLAUDE.md 为路由层（≤300行）；本文件为法典索引。
> 版本：4.0 | 五阶段×三层矩阵架构 | 26仓库全量整合

---

## 架构公式

```
RUNTIME = superpowers(methodology) + GSD(context) + OpenSpec(spec) + gstack(review) + claude-mem(memory)
STRUCTURE = ECC(manifest) + anthropics/skills(format) + best-practice(entry)
OPTIMIZATION = RTK(shell) + caveman(output)
REVIEW = gstack 5角色 + gstack 7补全
```

## 五阶段处理流程

```
用户输入 → ①规划(/discuss) → ②规格(/plan) → ③执行(/execute) → ④验证(/verify) → ⑤学习(/compact)
              │                  │               │                 │                  │
          HARD-GATE          spec-valid       子agent          质量门+审查       模式提取
```

每阶段嵌入三层加载：骨架层(always-on) + 执行层(reactive) + 横切层(cross-cutting)

---

## 五柱声明

| 柱 | 来源 | 职责 | 本地位置 |
|----|------|------|----------|
| Superpowers | obra/superpowers | 方法论 + P0 skill + HARD-GATE | skills/×13, hooks/bootstrap |
| GSD | gsd-build/get-shit-done | 上下文工程 + 三级阈值 + read-before-edit | rules/CONTEXT, templates/planning/ |
| OpenSpec | Fission-AI/OpenSpec | 规格格式 proposal→spec→tasks | templates/openspec/, spec-validation |
| gstack | garrytan/gstack | 角色审查 5+7 + 浏览器QA | agents/×12, autoplan/ship |
| claude-mem | thedotmack/claude-mem | 跨会话记忆 SSOT + 渐进式披露 | plugins/marketplaces/thedotmack/ |

---

## 规模约束

| 类型 | 上限 | 当前 |
|------|------|------|
| 全局 skills | ≤28 | 27 (superpowers 13 + 扩展 8 + meta 4 + mattpocock 2) |
| 全局 agents | ≤22 | 20 (core 8 + gstack审查 5 + gstack补全 7) |
| 全局 rules | 10 | 10 (CORE + BESTPRACTICE + SECURITY + GIT + WORKFLOW + AGENTS + MCP + DESIGN + CONTEXT + README) |
| CLAUDE.md | ≤300 | ~260 |
| 全局 hooks | 15 | 15 |

---

## P0 强制 Skill (4)

| Skill | 触发 | 阶段 |
|-------|------|------|
| using-superpowers | 会话开始 | 骨架 |
| brainstorming | 方案/架构/非简单任务 | ①规划 |
| verification-before-completion | 完成/验收 | ④验证 |
| systematic-debugging | 调试/bug | ③执行 |

## Workflow Skills (13 superpowers + 8 扩展 + 4 meta + 2 mattpocock)

**Superpowers 13**：using-superpowers, brainstorming, writing-plans, executing-plans, verification-before-completion, systematic-debugging, test-driven-development, subagent-driven-development, using-git-worktrees, receiving-code-review, requesting-code-review, finishing-a-development-branch, writing-skills

**扩展 8**：office-hours, autoplan, browser-qa, design-pipeline, ship, context-engineering, structured-artifacts, instinct-learning

**Meta 4**：memory-compression, spec-validation, karpathy-guidelines, caveman-compress

**Mattpocock 2**：triage, improve-codebase-architecture

---

## 核心 Agents (8)

| Agent | 预加载 skill | 阶段 |
|-------|-------------|------|
| planner | writing-plans | ①规划 |
| code-explorer | — | ③执行 |
| code-reviewer | requesting/receiving-code-review | ④验证 |
| build-error-resolver | systematic-debugging | ③执行 |
| architect | brainstorming | ①规划 |
| spec-reviewer | spec-validation | ②规格 |
| context-manager | memory-compression, caveman-compress | ⑤学习 |
| agentic-orchestrator | subagent-driven-development | ③执行 |

## gstack 审查 5 + 补全 7

**审查 (skeleton)**：eng-reviewer, ceo-reviewer, designer, qa, security-reviewer
**补全 (supplement)**：cso, sre, release-engineer, product-manager, design-engineer, performance-engineer, doc-writer

---

## 规格三轨（互斥）

| 轨道 | 路径 | 场景 | 入口 |
|------|------|------|------|
| OpenSpec | `openspec/changes/<id>/` | 功能变更/brownfield | /propose |
| GSD | `.planning/phases/` | 大功能多阶段 | /plan |
| 轻量 | `spec/<project>/` | ≤3文件小功能 | /plan |

---

## MCP 分组

| 分组 | 服务器 | 加载 |
|------|--------|------|
| always | memory, thinking, fs, fetch, time | 会话启动 |
| dev | gh, git, ctx7, pw, crawl, chrome-devtools | 开发会话 |
| ops | redis, sqlite, docker, postgres | 需要时 |
| search | brave, exa | 搜索时 |
| design | figma | 设计时 |
| optional | puppeteer, glif | 明确触发 |

权威 → `.mcp.json` | 分组 → `mcp/servers.json`

---

## Hooks (15核心)

| 事件 | Hook | 阶段 |
|------|------|------|
| SessionStart | bootstrap | 骨架 |
| PreToolUse/Bash | rtk-rewrite, bash-guard | ③执行 |
| PreToolUse/Write | read-before-edit, config-protection | ③执行 |
| PreToolUse/全局 | context-injector, manifest-validator | 全流程 |
| PostToolUse/Edit | secret-detector, edit-format | ④验证 |
| PostToolUse/全局 | operation-log | 全流程 |
| PreCompact | compact-state | ⑤学习 |
| Stop | quality-gate, pattern-extraction, session-summary, readme-updater | ⑤学习 |

Profile: `ECC_HOOK_PROFILE=standard` (minimal/standard/strict)

---

## 26+ 仓库完整映射

### 五柱 (5)

| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 1 | obra/superpowers | 14技能+HARD-GATE+双阶段审查+证据驱动 | skills/×13, hooks/ |
| 2 | gsd-build/get-shit-done | 可grep规则+三级阈值+read-before-edit | rules/CONTEXT, templates/planning/ |
| 3 | Fission-AI/OpenSpec | proposal→spec→tasks+brownfield+archive | templates/openspec/, spec-validation |
| 4 | garrytan/gstack | 5角色审查+7补全+浏览器QA | agents/×12 |
| 5 | thedotmack/claude-mem | 渐进式披露+向量搜索+6hook SSOT | plugins/marketplaces/thedotmack/ |

### 结构格式 (6)

| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 6 | affaan-m/ECC | MANIFEST+agent路由+instinct-learning | MANIFEST, agent.yaml, catalog/ |
| 7 | anthropics/skills | SKILL.md格式标准+跨平台 | skills/*/SKILL.md |
| 8 | shanraisshan/best-practice | 80+提示+10+方法论+编排模式 | rules/BESTPRACTICE |
| 9 | forrestchang/karpathy | 四原则+LLM失效模式对策 | rules/CORE, karpathy-guidelines |
| 10 | mattpocock/skills | triage分诊+grill反推+DDD重构+handoff | skills/triage, improve-codebase-architecture |
| 11 | VoltAgent/awesome-design-md | 9节结构+73品牌+零依赖 | rules/DESIGN, templates/DESIGN.md |

### 优化工具 (4)

| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 12 | rtk-ai/rtk | Rust CLI 60-90%压缩+100+命令预置 | hooks/pre-rtk-rewrite |
| 13 | JuliusBrussee/caveman | 四级压缩+仅压输出+学术佐证 | skill/caveman-compress |
| 14 | github/github-mcp-server | 20+工具+Enterprise+精细权限 | .mcp.json (gh) |
| 15 | anthropics/claude-code-action | 4后端CI+结构化JSON | templates/github-actions/ |

### 编排增强 (4)

| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 16 | eyaltoledano/task-master | PRD→结构任务+3级工具裁剪 | templates/taskmaster/ |
| 17 | nextlevelbuilder/ui-ux-pro-max | 67风格+161色板+99UX | catalog/skills/ui-ux-pro-max |
| 18 | zilliztech/claude-context | Milvus+BM25+40% token节省 | mcp-configs/ optional |
| 19 | bytedance/deer-flow | 渐进式加载+Docker沙箱+DAG | WORKFLOW.md |

### 参考索引 (5)

| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 20 | ComposioHQ/awesome-claude-skills | 1000+技能索引+渐进式加载 | catalog/ 索引 |
| 21 | hesreallyhim/awesome-claude-code | 配置范式+工具发现 | 外链索引 |
| 22 | x1xhlol/system-prompts | 30+提示词比较+注入防护 | BESTPRACTICE 原则 |
| 23 | Chalarangelo/30-seconds-of-code | 多语言代码片段 | catalog 参考 |
| 24 | ruvnet/ruflo | 蜂群拓扑+HNSW加速 | 概念→WORKFLOW |

### 安全补强 (4)

| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 25 | trailofbits/claude-code-config | /sandbox+deny+三层防御 | SECURITY.md §11 |
| 26 | dwarvesf/claude-guardrails | 密钥扫描 | hooks/_optional/ |
| 27 | lasso-security/claude-hooks | 注入扫描 | hooks/_optional/ |
| 28 | marc-shade/claude-code-security | 渐进硬化checklist | SECURITY.md §14 |

---

## 防互博速查

| 场景 | Owner | 禁止 |
|------|-------|------|
| 计划 | skill/writing-plans | pre-task-planner, agentic-orchestrator |
| 审查 | requesting/receiving-code-review | 独立 code-review skill |
| 记忆 | claude-mem plugin | memory MCP 作 SSOT |
| Shell token | hook/pre-rtk-rewrite | skill 重复压缩 |
| 输出 token | skill/caveman-compress | RTK 压缩 agent 文本 |
| 功能 spec | openspec/ | .planning 同功能重写 |
| plugin vs skill | MANIFEST concern→owner | plugin 替代已有 skill 同名功能 |
| hook vs plugin | settings.json hooks | plugin hook 与全局 hook 同事件链重复 |
| context-manager | agent/context-manager | 重复 claude-mem 存储逻辑 |

---

## Catalog（按需）

| 目录 | 规模 | 加载 |
|------|------|------|
| catalog/skills/ | ~120 | 按需 `python scripts/migrate-from-legacy.py --skill` |
| catalog/agents/ | 43 | 按需 `python scripts/migrate-from-legacy.py --agent` |
| catalog/rules/ | ~15 | 按需 `python scripts/migrate-from-legacy.py --rule` |

---

## 同步

| 同步 | 方式 |
|------|------|
| CLAUDE.md, AGENTS.md, skills/, agents/ | 软链接 (sync.ps1) |
| rules/ | 格式转换到编辑器原生目录 |
| hooks/, commands/, MCP | ❌ 不同步 |

---

_版本：4.0 | 日期：2026-05-27 | 五阶段×三层矩阵架构 | 28仓库全量整合_
