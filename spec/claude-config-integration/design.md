# Design — .claude 配置整合架构

> **设计源**：25 个 GitHub 仓库 PRIMARY + P3 安全补强 → 五柱 × 五阶段 × 三层
> **版本**：3.0 | **日期**：2026-05-27 | **关联**：[spec.md](./spec.md) | [tasks.md](./tasks.md)

---

## 1. 架构总览

```
用户输入 → ①规划 → ②规格 → ③执行 → ④验证 → ⑤学习
              │       │       │       │       │
         ┌────┴───────┴───────┴───────┴───────┴────┐
         │  骨架层(always-on) + 执行层(reactive)      │
         │        + 横切层(cross-cutting)            │
         └──────────────────────────────────────────┘
```

### 1.1 五阶段门控

| 阶段 | 命令入口 | 五柱主导 | 门控 |
|------|---------|---------|------|
| ①规划 | /discuss | Superpowers | HARD-GATE 用户批准设计 |
| ②规格 | /plan | OpenSpec | spec-validation + 成功标准明确 |
| ③执行 | /execute | GSD | 子任务完成 + 构建/类型/Lint通过 |
| ④验证 | /verify | gstack | 质量门全通过 + 交叉验证清单 |
| ⑤学习 | /compact | claude-mem | 模式提取 + 上下文释放 |

### 1.2 三层加载

| 层 | 加载时机 | Token占比 | 内容 |
|----|---------|-----------|------|
| 骨架层 | SessionStart一次性 | ~5% | CORE.md + using-superpowers + 安全门 + claude-mem init |
| 执行层 | 按阶段触发 | 增量 | P0 skill → workflow skill → agent → MCP tool |
| 横切层 | 事件驱动贯穿 | 事件驱动 | RTK(token) + caveman(输出) + 质量门 + 安全扫描 |

---

## 2. 五柱定义

| 柱 | PRIMARY | 职责 | Owner | 禁止 |
|----|---------|------|-------|------|
| Superpowers | obra/superpowers | 方法论 + P0 skill + HARD-GATE | skills/ | hook替代skill决策 |
| GSD | gsd-build/get-shit-done | 上下文阈值 + read-before-edit + 子agent调度 | rules/CONTEXT | 多处重复阈值 |
| OpenSpec | Fission-AI/OpenSpec | 规格格式 proposal→spec→tasks | templates/openspec + spec-validation | 同功能占用多轨 |
| gstack | garrytan/gstack | 角色审查 5+7 + 浏览器QA | agents/ | superpowers审查skill |
| claude-mem | thedotmack/claude-mem | 跨会话记忆 SSOT + 渐进式披露 | plugin/ | memory MCP作SSOT |

### 2.1 辅助层

| 层 | PRIMARY | 职责 |
|----|---------|------|
| 结构 | affaan-m/ECC | MANIFEST + agent.yaml + catalog + profile |
| 格式 | anthropics/skills | SKILL.md frontmatter 标准 |
| 入口 | shanraisshan/best-practice + karpathy | CLAUDE.md 路由 ≤300行 |
| 优化 | rtk-ai/rtk + JuliusBrussee/caveman | Token 双轨 Shell+输出 |
| 设计 | VoltAgent/awesome-design-md | DESIGN.md token |
| 工程 | mattpocock/skills | triage + improve-codebase-architecture |

---

## 3. 五阶段 × 三层 操作手册

### ① 规划阶段

```
骨架: CLAUDE.md 优先级链 + R1-R11 + CORE.md
执行: brainstorming → writing-plans → agent/planner
      └─ grill-with-docs (mattpocock) 反推需求明确
      └─ ceo-reviewer (gstack) 大功能产品审查
横切: RTK(token) + 上下文阈值<40%
门控: HARD-GATE 用户批准设计 ✓
```

### ② 规格阶段

```
骨架: 三轨声明 (OpenSpec/GSD/轻量)
执行: spec-validation → agent/spec-reviewer
      ├─ OpenSpec → openspec/changes/<id>/ (proposal/specs/design/tasks)
      ├─ GSD      → .planning/phases/
      └─ 轻量     → spec/<project>/
      └─ designer (gstack) UI变更时
横切: 安全扫描 + caveman(讨论收束) + pre-manifest-validator
门控: spec-validation通过 + 任务有成功标准 + 无静默缩scope
```

### ③ 执行阶段

```
骨架: R10+R11 + read-before-edit + pre-bash-guard + pre-config-protection
执行: executing-plans → subagent-driven-development
      ├─ 简单(≤3文件) → 主会话直接实现
      └─ 复杂 → agentic-orchestrator → 并行子Agent(200K fresh context)
      MCP按需: ctx7文档/git版本/pw浏览器/gh PR
横切: RTK(Shell输出) + caveman(Agent输出) + 50%→compact建议
门控: 子任务完成 + 构建/类型/Lint通过
```

### ④ 验证阶段

```
骨架: R1(验证才算完成) + R7(交叉验证) + 质量门
执行: verification-before-completion
      ├─ 代码验证: 构建/类型/Lint/无调试残留
      ├─ 安全验证: 无硬编码密钥/注入/权限
      ├─ 质量门: schema_drift/security_anchor/scope_reduction
      └─ gstack审查: eng-reviewer(必须) + ceo/designer/security(按需)
横切: post-secret-detector + 70%→强制压缩
门控: 质量门全通过 + 交叉验证通过
```

### ⑤ 学习阶段

```
骨架: claude-mem 持久化
执行: stop-pattern-extraction → writing-skills
      ├─ 成功模式 → experiences/patterns/
      └─ 失败模式 → experiences/rejected/
      stop-session-summary + stop-readme-updater
横切: 上下文释放 + pre-compact-state
门控: 模式提取完成
```

---

## 4. 25 仓库优点整合

### 4.1 五柱骨架 (5)

| # | 仓库 | 核心优点 | 落地 |
|---|------|---------|------|
| 1 | obra/superpowers | 14技能闭环 + HARD-GATE + 双阶段审查 + 证据驱动 | skills/×13, hooks/ |
| 2 | gsd-build/get-shit-done | 可grep规则 + 三级阈值 + read-before-edit + 合并波 | rules/CONTEXT, templates/planning/ |
| 3 | Fission-AI/OpenSpec | proposal→spec→tasks + brownfield友好 + archive | templates/openspec/, spec-validation |
| 4 | garrytan/gstack | 5角色审查+7补全 + 浏览器QA + 六层安全 | agents/×12, autoplan/ship |
| 5 | thedotmack/claude-mem | 渐进式披露 + 向量+关键词混合搜索 + 6hook SSOT | plugins/marketplaces/thedotmack/ |

### 4.2 结构格式 (6)

| # | 仓库 | 核心优点 | 落地 |
|---|------|---------|------|
| 6 | affaan-m/ECC | MANIFEST归属 + 61agent/246skill库 + instinct-learning | MANIFEST, agent.yaml, catalog/ |
| 7 | anthropics/skills | SKILL.md格式标准 + 跨平台 + Apache 2.0 | skills/*/SKILL.md |
| 8 | shanraisshan/best-practice | 80+提示 + 10+方法论 + 编排模式文档 | rules/BESTPRACTICE |
| 9 | forrestchang/karpathy | 四原则 + 跨工具 + LLM失效模式对策 | rules/CORE, karpathy-guidelines |
| 10 | mattpocock/skills | triage分诊 + grill反推需求 + DDD重构 + handoff | skills/triage, improve-codebase-architecture |
| 11 | VoltAgent/awesome-design-md | 9节结构 + 73品牌 + 零依赖 | rules/DESIGN, templates/DESIGN.md |

### 4.3 优化工具 (4)

| # | 仓库 | 核心优点 | 落地 |
|---|------|---------|------|
| 12 | rtk-ai/rtk | Rust CLI 60-90% Shell压缩 + 100+命令预置 | hooks/pre-rtk-rewrite |
| 13 | JuliusBrussee/caveman | 四级压缩 + 仅压输出 + 学术佐证 | skill/caveman-compress |
| 14 | github/github-mcp-server | 20+工具 + Enterprise Server + 精细权限 | .mcp.json (gh) |
| 15 | anthropics/claude-code-action | 4后端CI + 结构化JSON输出 | templates/github-actions/ |

### 4.4 编排增强 (4)

| # | 仓库 | 核心优点 | 落地 |
|---|------|---------|------|
| 16 | eyaltoledano/claude-task-master | PRD→结构化任务 + 3级工具裁剪(5K/10K/21K) | writing-plans 模板参考 |
| 17 | nextlevelbuilder/ui-ux-pro-max | 67风格 + 161色板 + 99UX指南 + Design System Generator | catalog/skills/ui-ux-pro-max |
| 18 | zilliztech/claude-context | Milvus+BM25搜索 + AST分块 + 40% token节省 | mcp-configs/ optional |
| 19 | bytedance/deer-flow | 渐进式加载 + Docker沙箱 + DAG编排 | WORKFLOW.md |

### 4.5 参考索引 (6)

| # | 仓库 | 吸收 | 落地 |
|---|------|------|------|
| 20 | ComposioHQ/awesome-claude-skills | 1000+技能索引 + 渐进式加载 | catalog/ 发现索引 |
| 21 | hesreallyhim/awesome-claude-code | 配置范式 + 工具发现 | SPEC.md 外链 |
| 22 | x1xhlol/system-prompts | 30+工具提示词比较 + 注入防护 | BESTPRACTICE 原则 |
| 23 | Chalarangelo/30-seconds-of-code | 多语言代码片段 | catalog 参考 |
| 24 | ruvnet/ruflo | 蜂群拓扑 + HNSW记忆加速 | 概念吸收→WORKFLOW |

### 4.6 P3 安全补强

| 仓库 | 吸收 | 落地 |
|------|------|------|
| trailofbits/claude-code-config | /sandbox + deny + 三层防御 | SECURITY.md §11 |
| dwarvesf/claude-guardrails | UserPromptSubmit 密钥扫描 | hooks/_optional/ |
| lasso-security/claude-hooks | 注入模式扫描 | hooks/_optional/ |
| marc-shade/claude-code-security | 渐进硬化checklist | SECURITY.md §14 |

---

## 5. 防互博

### 5.1 机制

```
pre-manifest-validator.py (PreToolUse):
  解析 intent → 查 MANIFEST.concerns.<intent>.owner
  → 查 excludes → 当前 agent/skill 在 excludes 中 → block
  → 当前 agent/skill ≠ owner → warn
```

### 5.2 互斥规则

| Concern | Owner | Excludes |
|---------|-------|----------|
| planning | skill/writing-plans | pre-task-planner, agent/agentic-orchestrator |
| brainstorming | skill/brainstorming | agent/planner |
| memory | plugin/claude-mem | agent/context-manager |
| shell_token | hook/pre-rtk-rewrite | skill 重复压缩 |
| output_token | skill/caveman-compress | hook 重复压缩 |
| change_spec | openspec/changes/ | planning/phases 同功能 |
| phase_planning | planning/phases/ | openspec/changes 同功能 |

---

## 6. MCP 按需加载

```
always (5):  memory, thinking, fs, fetch, time
+ dev (6):   gh, git, ctx7, pw, crawl, chrome-devtools
+ ops (3):   redis, sqlite, docker
+ search (3): brave, exa, perplexity
+ design (1): figma
+ optional (3): postgres, puppeteer, glif
```

默认: always + env("CLAUDE_MCP_PROFILE") 指定分组

---

## 7. Hooks 精简

| 事件 | 精简前 | 精简后 | 变化 |
|------|--------|--------|------|
| SessionStart | 1 | 1 | — |
| PreToolUse | 8 | 6 | +manifest-validator, 合并dep-checker/block至bash-guard |
| PostToolUse | 7 | 3 | 删test-runner/doc-reminder, 合并lint至format |
| PreCompact | 1 | 1 | — |
| Stop | 7 | 4 | 删notify/debug-checker/daily-summary |
| **总计** | **24** | **15** | -9 |

冗余hook移至 `hooks/_optional/`

---

## 8. 目录树 (v3.0)

```
~/.claude/
├── CLAUDE.md                    # 路由入口 (≤300行)
├── SPEC.md                      # 法典索引
├── MANIFEST.yaml                # concern→owner
├── agent.yaml                   # harness清单
├── .mcp.json                    # MCP唯一源
├── settings.json                # env+permissions+hooks+model
│
├── rules/ (9)
│   ├── CORE.md                  # alwaysApply: R1-11+Karpathy
│   ├── BESTPRACTICE.md          # alwaysApply: 综合最佳实践
│   ├── SECURITY.md              # lazy
│   ├── GIT.md                   # lazy
│   ├── WORKFLOW.md              # lazy
│   ├── AGENTS.md                # lazy
│   ├── MCP.md                   # lazy
│   ├── DESIGN.md                # lazy
│   └── CONTEXT.md               # lazy
│
├── skills/ (27)
│   ├── SKILL.md                 # 索引: 名称→触发→路径
│   ├── brainstorming/           # P0
│   ├── using-superpowers/       # P0
│   ├── verification-before-completion/ # P0
│   ├── systematic-debugging/    # P0
│   ├── writing-plans/ ...       # workflow ×13
│   ├── autoplan/ ...            # 扩展 ×8
│   ├── memory-compression/ ...  # meta ×4
│   └── triage/ ...              # mattpocock ×2
│
├── agents/ (20)
│   ├── README.md
│   ├── planner.md, code-explorer.md ... # core ×8
│   ├── eng-reviewer.md ...             # gstack 审查 ×5
│   └── cso.md, sre.md ...              # gstack 补全 ×7
│
├── hooks/ (15核心)
│   ├── session-start-bootstrap.py
│   ├── pre-context-injector.py
│   ├── pre-rtk-rewrite.py
│   ├── pre-bash-guard.py
│   ├── pre-read-before-edit.py
│   ├── pre-config-protection.py
│   ├── pre-manifest-validator.py  # 新增
│   ├── post-secret-detector.py
│   ├── post-edit-format.py
│   ├── post-operation-log.py
│   ├── pre-compact-state.py
│   ├── stop-quality-gate.py
│   ├── stop-pattern-extraction.py
│   ├── stop-session-summary.py
│   └── stop-readme-updater.py
│
├── templates/
│   ├── openspec/    (proposal/specs/design/tasks)
│   ├── planning/    (GSD phases)     ← 补齐
│   ├── spec/        (轻量spec)       ← 补齐
│   ├── taskmaster/
│   ├── DESIGN.md
│   └── github-actions/
│
├── catalog/         (100 skills / 43 agents 按需)
├── experiences/     (patterns/ + rejected/)
├── mcp-configs/     (按分组加载)
├── config/          (quality_gates.json)
├── commands/        (14)
├── plugins/         (claude-mem)
└── scripts/         (sync/validate/migrate)
```

---

## 9. SSOT 声明

| 内容 | 唯一源 | 其他只能 |
|------|--------|---------|
| MCP定义 | .mcp.json | pointer |
| 铁律 R1-R11 | rules/CORE.md | pointer |
| concern归属 | MANIFEST.yaml | 引用 |
| 跨会话记忆 | claude-mem DB/Chroma | pointer |
| skill定义 | skills/*/SKILL.md | agent写preload列表 |
| agent定义 | agents/*.md | skill不重复agent指令 |
| UI token | DESIGN.md | frontend skill引用 |
| 功能spec | openspec/ \| .planning/ \| spec/ | CLAUDE.md不抄需求 |

---

## 10. 持续学习闭环

```
任务完成 → stop-pattern-extraction → patterns/ (0.7-0.9)
                                     → instincts/ (≥0.9)
                                     → rejected/ (<0.5)
         → claude-mem 压缩观察 → SQLite+Chroma
         → /compact → pre-compact-state 快照

新会话 → session-start-bootstrap → 注 claude-mem 记忆
       → 查 catalog/skills/ 匹配领域 skill
```

---

_版本：3.0 | 日期：2026-05-27 | 五阶段×三层矩阵架构_
