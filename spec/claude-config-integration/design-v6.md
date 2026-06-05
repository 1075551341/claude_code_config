# Design v6.0 — 五柱 × 五阶段 × 三横切 架构（27 仓库全量重新调研）

> 日期: 2026-06-05 | 基于 27 仓库全量重新抓取 + brainstorming 四轮决策 | 替代 design-v5.md
> 关联: [spec.md](./spec.md) | [tasks-v6.md](./tasks-v6.md)

---

## 1. 架构公式

```
CLAUDE = 五柱(纵向阶段驱动) × 五阶段(流程) × 三横切(基础设施)

五柱:
  Superpowers   — 方法论 (brainstorming → plan → execute → verify)
  GSD           — 上下文工程 (三级阈值 + read-before-edit + phase)
  OpenSpec      — 规格格式 (propose → spec → tasks → archive)
  gstack        — 角色审查 (CEO/设计/工程/QA/安全 + iOS/注入防御/品味记忆)
  claude-mem    — 跨会话记忆 (渐进式披露 SSOT)

五阶段:
  ① 规划 → ② 规格 → ③ 执行 → ④ 验证 → ⑤ 学习

三横切 (所有阶段常驻基础设施):
  L1 治理 — ECC(防互博+选择性安装+hook分级+loop防护) + deer-flow 2.0(LangGraph编排)
  L2 优化 — RTK(shell压缩,60-90%) + caveman(输出压缩,~75%) + 三级阈值(上下文治理)
  L3 洞察 — codegraph(静态索引,47% token减少) + Understand-Anything(交互知识图) + Firecrawl/Exa(外部搜索)
```

### 1.1 相对 v5.2 的核心变更

| # | 变更 | v5.2 | v6.0 | 原因 |
|---|------|------|------|------|
| 1 | **架构模型** | 五柱 + 三层补充 | 五柱 × 五阶段 × 三横切 | L1/L2/L3 是横切基础设施，不是柱的附属 |
| 2 | **ECC 定位** | "结构格式"参考 | L1 治理层核心引擎 | v2.0.0-rc.1 已是完整 operator 系统(63 agents + 251 skills + Rust 控制平面) |
| 3 | **gstack 规模** | 5审查 + 7补全 | +iOS专用 +ML注入防御 +跨模型审查 +品味记忆 | v0.19 新增能力 |
| 4 | **deer-flow** | DAG+middleware chain | LangGraph 2.0 + claude-to-deerflow 桥接 | 2.0 ground-up rewrite |
| 5 | **gsd 源** | gsd-build/get-shit-done | open-gsd/gsd-core v1.42.3 | 仓库已迁移 |
| 6 | **加载策略** | 文件级 alwaysApply/lazy | 骨架(CLAUDE+CORE) + paths: glob + 渐进披露 | 精确 token 控制 |
| 7 | **vibe-coding-cn** | 缺口 G6 | 道/法/术/器 + α/Ω 元技能 | 中文协作方法论成熟 |
| 8 | **codegraph 数据** | "~35% token节省" | 7仓库实测: 47% token减少, 58%调用减少, 16%成本降低 | 精确基准数据 |

---

## 2. 27 仓库落点（三层分类）

### 2.1 五柱（5）

| # | 仓库 | 版本 | 核心吸收 | 本地位置 |
|---|------|------|----------|----------|
| 1 | obra/superpowers | 5.1.0 | 14技能闭环 + HARD-GATE + SessionStart bootstrap | skills/×13, hooks/session-start-bootstrap |
| 2 | open-gsd/gsd-core | 1.42.3 | 上下文工程 + 三级阈值 + read-before-edit | rules/CONTEXT.md, templates/planning |
| 3 | Fission-AI/OpenSpec | 1.4.1 | proposal→spec→tasks→archive + 25+AI工具 | templates/openspec, skill/spec-validation |
| 4 | garrytan/gstack | 0.19 | 审查(CEO/设计/工程/QA/安全/SRE)+iOS+注入防御+品味记忆 | agents/×20+, skills/autoplan/ship/office-hours |
| 5 | thedotmack/claude-mem | 13.4.0 | 渐进式披露 + 三层检索(search→timeline→get) + ~10x token节省 | plugins/claude-mem + MCP memory tools |

### 2.2 三横切（3+1）

| # | 仓库 | 层 | 核心吸收 | 本地位置 |
|---|------|----|----------|----------|
| 6 | affaan-m/ECC | L1治理 | concern→owner→excludes防互博 + hook profile分级 + observer loop防护 + 选择安装 | MANIFEST.yaml, agent.yaml, hooks/ |
| 7 | bytedance/deer-flow 2.0 | L1治理 | LangGraph编排 + flash/standard/pro/ultra四模式 + claude-to-deerflow桥接 | rules/WORKFLOW.md |
| 8 | rtk-ai/rtk | L2优化 | Rust CLI 60-90% Shell压缩 + 100+命令预置 + v0.42.1 | hooks/pre-rtk-rewrite, RTK.md |
| 9 | JuliusBrussee/caveman | L2优化 | 四级输出压缩(lite/full/ultra/wenyan) + ~75%节省 + v1.8.2 | skill/caveman-compress |
| — | 三级阈值 | L2优化 | <40%/50%/70% 上下文腐烂治理 | rules/CONTEXT.md → 骨架迁入 CORE.md |
| 10 | colbymchenry/codegraph | L3洞察 | 预索引代码图谱 MCP + 47% token减少 + 58%调用减少 + v0.9.9 | .mcp.json + .codegraph/ |
| 11 | Lum1104/Understand-Anything | L3洞察 | 交互知识图 + 5 Agent管线 + 引导导览 + v2.7.3 | plugins/ + skill/understand-anything |

### 2.3 格式标准（5）

| # | 仓库 | 核心吸收 | 本地位置 |
|---|------|----------|----------|
| 12 | anthropics/skills | SKILL.md 格式标准(YAML frontmatter + Markdown) + 三平台(Code/API/Web) | 所有 skill 遵守此格式 |
| 13 | shanraisshan/claude-code-best-practice | paths: glob lazy-load + 六机制 + `<important if>` 标签 | rules/BESTPRACTICE.md |
| 14 | forrestchang/andrej-karpathy-skills | 四原则 + LLM失效模式对策 | skill/karpathy-guidelines, rules/CORE.md |
| 15 | mattpocock/skills | triage状态机 + grill反推 + improve-architecture | skill/triage, skill/improve-codebase-architecture |
| 16 | 2025Emma/vibe-coding-cn | 道/法/术/器框架 + α(生成器)/Ω(优化器)元技能 + 五步协作流程 | catalog/skills/vibe-coding-cn |

### 2.4 补充技能（3）

| # | 仓库 | 核心吸收 | 本地位置 |
|---|------|----------|----------|
| 17 | eyaltoledano/claude-task-master | PRD→结构化任务 + MCP协议 + 3级工具裁剪 | templates/taskmaster |
| 18 | nextlevelbuilder/ui-ux-pro-max | 67 UI风格 + 161色板 + 99 UX指南 + v2.0设计系统生成器 | catalog/skills/ui-ux-pro-max |
| 19 | VoltAgent/awesome-design-md | 9节DESIGN.md结构 + 72品牌 + YAML token | rules/DESIGN.md + templates/DESIGN.md |

### 2.5 工具集成（3）

| # | 仓库 | 核心吸收 | 本地位置 |
|---|------|----------|----------|
| 20 | github/github-mcp-server | 16 toolsets + 细粒度权限 + lockdown模式 | .mcp.json (gh) |
| 21 | anthropics/claude-code-action | 4云后端 + 智能模式检测 + 结构化JSON输出 + v1.0 | templates/github-actions |
| 22 | zilliztech/claude-context | Milvus+BM25混合搜索 + ~40% token节省 | .mcp.json optional分组 |

### 2.6 参考索引（5）

| # | 仓库 | 核心吸收 | 本地位置 |
|---|------|----------|----------|
| 23 | ComposioHQ/awesome-claude-skills | 1000+ 技能索引 + 渐进式加载模式 | catalog/ 索引参考 |
| 24 | hesreallyhim/awesome-claude-code | 配置范式 + 工具发现（重构中） | 外链索引 |
| 25 | x1xhlol/system-prompts-and-models | 30+提示词比较 + ZeroLeaks注入防护 | BESTPRACTICE 原则吸收 |
| 26 | Chalarangelo/30-seconds-of-code | 多语言代码片段 + v14.0.0 | catalog/ 参考 |
| 27 | ruvnet/ruflo | 蜂群拓扑 + HNSW向量记忆 + 3共识 + v3.10.34 | 概念吸收→WORKFLOW.md（不落地） |

---

## 3. 五阶段 × 三横切 操作手册

### ① 规划阶段

```
骨架: CLAUDE.md 优先级链 + rules/CORE.md (铁律+阈值)
执行: brainstorming → writing-plans → agent/planner
      ├─ grill-with-docs (mattpocock) 反推需求明确
      ├─ ceo-reviewer (gstack) 大功能产品审查
      ├─ codegraph 探索代码结构
      └─ Understand-Anything 导览架构概念
横切: L1(MANIFEST防互博+hook分级) + L2(RTK压缩+阈值检查<40%) + L3(codegraph/UA/Firecrawl调研)
门控: HARD-GATE 用户批准设计 ✓
```

### ② 规格阶段

```
骨架: 三轨声明 (OpenSpec/GSD/轻量)
执行: spec-validation → agent/spec-reviewer
      ├─ OpenSpec → openspec/changes/<id>/
      ├─ GSD      → .planning/phases/
      └─ 轻量     → spec/<project>/
      └─ designer (gstack) UI变更 + DESIGN.md token规范
横切: L1(pre-manifest-validator) + L2(caveman讨论收束) + L3(Understand-Anything查设计模式)
门控: spec-validation通过 + 任务有成功标准 + 无静默缩scope
```

### ③ 执行阶段

```
骨架: rules/CORE.md(R10+R11+R16) + read-before-edit
执行: executing-plans → subagent-driven-development
      ├─ 简单(≤3文件) → 主会话直接实现
      └─ 复杂 → agentic-orchestrator → 并行子Agent(200K fresh context)
      MCP按需: ctx7文档/git版本/pw浏览器/gh PR/codegraph结构/UA概念
横切: L1(agent.yaml调度+deer-flow DAG) + L2(RTK Shell+caveman输出+50%→compact) + L3(codegraph探索)
门控: 子任务完成 + 构建/类型/Lint通过 + 子Agent异常已处理(R16)
```

### ④ 验证阶段

```
骨架: R1(验证才算完成) + R7(交叉验证) + 质量门
执行: verification-before-completion
      ├─ 代码验证: 构建/类型/Lint/无调试残留
      ├─ 安全验证: post-secret-detector + 无硬编码密钥
      ├─ 质量门: schema_drift/security_anchor/scope_reduction
      ├─ 错误暴漏: 裸except:pass扫描=0(R16)
      └─ gstack审查: eng-reviewer(必须) + ceo/designer/security/iOS(按需)
横切: L1(loop防护+context上限) + L2(caveman-review) + L3(codegraph impact分析)
门控: 质量门全通过 + 交叉验证通过
```

### ⑤ 学习阶段

```
骨架: claude-mem 持久化 SSOT
执行: stop-pattern-extraction → writing-skills
      ├─ 成功模式 → experiences/patterns/
      ├─ 失败模式 → experiences/rejected/
      └─ gstack /learn 跨会话学习(项目级) + claude-mem(会话级)互补
横切: L2(上下文释放+pre-compact-state) + L3(知识图更新)
门控: 模式提取完成
```

---

## 4. 加载策略（骨架精确控制）

### 4.1 三层加载模型

```
骨架层 (always-on, ~200 lines):
  CLAUDE.md          — 入口指针 + 优先级链 + 铁律摘要
  rules/CORE.md       — 编码规范 + 铁律R12-R16 + Karpathy四原则 + 三级阈值

执行层 (lazy, paths: glob 触发):
  rules/SECURITY.md   — paths: ["**/*.py","**/*.ts","**/*.js","**/*.go","**/*.rs"]
  rules/GIT.md        — paths: [".git/**"]
  rules/WORKFLOW.md   — 触发: Agent tool + skill/writing-plans + skill/subagent-driven-development
  rules/AGENTS.md     — 触发: Agent tool + subagent invocation
  rules/MCP.md        — 触发: .mcp.json edit + mcp server modify
  rules/DESIGN.md     — 触发: UI/frontend design tasks
  rules/BESTPRACTICE.md — 触发: implementation tasks (error handling, API design, logging)

补充层 (supplement, 显式按需):
  catalog/skills/     — 仅当匹配 task 时加载
  templates/          — 仅当 init/new 时引用
  plugins/            — 仅 name+description 预加载 (~100 tokens/skill)，完整 SKILL.md 按需拉取
```

### 4.2 骨架内容迁移

从 CONTEXT.md/WORKFLOW.md/BESTPRACTICE.md 提取骨架级内容迁入 CORE.md：

| 源文件 | 迁入 CORE.md 的内容 | 行数 |
|--------|---------------------|------|
| CONTEXT.md | 三级阈值 <40%/50%/70% + 腐烂治理行动 | ~15行 |
| WORKFLOW.md | 五阶段定义 + 状态机(DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED) | ~20行 |
| BESTPRACTICE.md | 错误处理规范 + 铁律R14-R16 | ~15行 |

---

## 5. 治审分离（L1 治理 vs gstack 审查）

### 5.1 ECC 机制吸收（L1 治理层）

| ECC 机制 | 吸收方式 | 本地位置 |
|----------|----------|----------|
| concern→owner→excludes 防互博 | 已吸收 | MANIFEST.yaml |
| Hook profile 分级 (minimal/standard/strict) | 新增 | hooks/README.md + settings.json |
| Observer loop 防护 (5层守卫) | 新增 | hooks/ 超时 + 重入检测 |
| SessionStart 上下文上限 (8000→4000) | 新增 | hook/pre-context-injector.py |
| 选择性安装 | 概念吸收 | MANIFEST.yaml 标记 |
| 环境变量控制 hook 启停 | 新增 | settings.json + ECC_HOOK_PROFILE |

### 5.2 gstack v0.19 能力扩展

| 新增能力 | 来源 | 本地落地 |
|----------|------|----------|
| iOS 专用 (ios-qa/ios-fix/ios-design-review/ios-clean/ios-sync) | gstack v0.19 | agents/ 新增 (按需) |
| ML 注入防御 (22MB 本地分类器+canary tokens) | gstack v0.19 | rules/SECURITY.md §15 |
| 跨模型审查 (/codex — Codex 独立 review) | gstack v0.19 | agents/codex-reviewer.md |
| 品味记忆 (5%/周衰减, gstack-taste-update) | gstack v0.19 | experiences/taste/ |
| 领域技能 (domain-skill save, 3次成功解锁) | gstack v0.19 | catalog/skills/ |

### 5.3 边界声明

```
ECC 管的（治理/基础设施）:  MANIFEST归属 + Hook分级 + Loop防护 + 上下文上限 + 选择安装
gstack 管的（审查/应用）:   角色审查 + 浏览器QA + 注入防御 + 品味记忆 + iOS + 跨模型
互斥保证: MANIFEST concern→excludes 确保同一事务不超过一个 owner
```

---

## 6. vibe-coding-cn 道/法/术/器 吸收

| 维度 | 内容 | 本地落地 |
|------|------|----------|
| **道**(原则) | "凡是AI能做的不人工做"、"先结构后代码"、"上下文是第一性要素" | rules/CORE.md Karpathy四原则补充 |
| **法**(策略) | "接口先行实现后补"、"能抄不写不重复造轮子"、"文档即上下文" | skill/writing-plans 计划模板 |
| **术**(技巧) | "明确能改什么不能改什么"、"Debug给预期vs实际+最小复现" | skill/systematic-debugging 补充 |
| **器**(工具) | Cursor/Claude Code/Codex CLI/Warp/Neovim | 工具链已就位 |
| **α-提示词**(生成器) | 唯一职责:生成其他提示词或技能 | skill/writing-skills |
| **Ω-提示词**(优化器) | 唯一职责:优化其他提示词或技能 | skill/instinct-learning |
| **五步协作** | 设计文档→技术栈→实施计划→记忆库→分步执行 | 五阶段流程已覆盖 |

---

## 7. 同步策略

保持当前 sync.ps1 v12.0 的 A+B 混合方案：
- CLAUDE.md, AGENTS.md → 文件符号链接
- skills/, agents/ → 目录联接 (Junction)
- rules/ → 格式转换复制（Windsurf trigger格式 + 字符限制 + Cursor .mdc）

改进：在 rules/ 编辑后通过 post-edit-format hook 提示重跑 sync.ps1。

---

## 8. 规模约束

| 类型 | 上限 | v5.2 实际 | v6.0 目标 |
|------|------|-----------|-----------|
| skills | ≤28 | 28 | 28 (不增不减) |
| agents | ≤22 | 20 | 22 (gstack iOS + codex-reviewer) |
| rules | 10 | 10 | 10 |
| CLAUDE.md | ≤300行 | ~260 | ~220 (精炼) |
| hooks | ≤18 | 15 | 17 (+loop防护+context上限) |
| 仓库覆盖 | 27 | 28(含P3) | 27(去P3独立) |
| P0 skill | 4 | 4 | 4 |

---

## 9. 设计自审

- [x] 无占位符/TODO
- [x] 五柱+三横切 范畴清晰（柱=阶段驱动，横切=基础设施）
- [x] 治审分离（ECC vs gstack 边界明确）
- [x] 27 仓库全部有落点
- [x] 加载策略骨架精确（CLAUDE.md + CORE.md only）
- [x] 无左右互博（MANIFEST excludes 声明）
- [x] 各编辑器格式兼容（sync.ps1 已验证）
- [x] R16 错误暴漏覆盖所有层
- [x] vibe-coding-cn 道/法/术/器 全吸收
