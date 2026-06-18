# 29 仓库深度调研报告 v8.0

> 日期: 2026-06-07 | 方法: Exa 语义搜索 + README 直接抓取 + 交叉验证 | 覆盖: 全部 29 仓库（新增深度）
> 上一版: 28-repo-deep-research-v7.md → 本次重点补充 ECC 2.0/deer-flow/ruflo/task-master 深度分析

---

## 五柱骨架 — 企业级架构核心

### 1. obra/superpowers v5.1.0 — 方法论引擎

**定位**: 从对话第一秒就介入 — 不直接写代码，先问清楚要构建什么

**完整工作流链**:
```
brainstorming (HARD-GATE) → using-git-worktrees → writing-plans (2-5min原子)
→ subagent-driven-development → test-driven-development (RED-GREEN-REFACTOR)
→ requesting-code-review (两阶段) → finishing-a-development-branch
```

**14 个核心 Skill**:
- P0 强制: brainstorming, verification-before-completion, systematic-debugging, using-superpowers
- 工作流: writing-plans, executing-plans, subagent-driven-development, test-driven-development
- 协作: requesting-code-review, receiving-code-review, dispatching-parallel-agents
- 工具: using-git-worktrees, finishing-a-development-branch, writing-skills

**独有创新**:
- HARD-GATE 设计批准: 用户批准前禁止实现（这是最关键的护栏）
- 设计文档分块展示: 短到能真正阅读消化
- 计划清晰到"热情的初级工程师都能执行"
- 跨平台: Claude Code / Codex CLI / Cursor / Gemini CLI / Windsurf / Copilot CLI

**吸收要点**: P0 强制 skill 链、HARD-GATE 模式、两阶段审查、原子任务 (2-5min)

---

### 2. GSD (get-shit-done → open-gsd/gsd-core) — 上下文工程

**核心哲学**: 上下文是第一性要素 — 管理好上下文比写好代码更重要

**原仓库已归档**: gsd-build/get-shit-done → 迁移至 open-gsd/gsd-core

**核心机制**:
1. **三级阈值**: <40% 正常 / 50% compact / 70% 强制压缩
2. **三态制品通信**: openspec/ + .planning/ + memory/（禁止通过对话历史传递状态）
3. **DAG 编排**: 无依赖并行派发，有依赖等待前置，冲突检测
4. **Read-Before-Edit**: 编辑前必须 Read 文件
5. **Trust-But-Verify**: Agent 自述不可信，必须通过 API/git 直接验证
6. **Canonical Source Precedence**: CONTRIBUTING.md > ADR > CONTEXT.md > Agent 记忆

**独有创新**:
- 上下文腐烂三级阈值（业界首创）
- 子 Agent 间通过三态制品通信（非对话历史）
- 规范文档引用链优先级

**吸收要点**: 三级阈值、三态制品、DAG 编排、Trust-But-Verify、Canonical Source

---

### 3. Fission-AI/OpenSpec v1.4.1 — 规格格式

**核心哲学**: fluid not rigid, iterative not waterfall, brownfield first

**opsx 工作流**:
```
/opsx:propose → proposal.md + specs/ + design.md + tasks.md
/opsx:apply   → 逐任务实现
/opsx:archive → 归档 + spec 更新
```

**关键特性**:
- 每个变更独立文件夹隔离
- 支持 25+ AI 工具（不锁定平台）
- 全局 CLI: `npm install -g @fission-ai/openspec@latest`
- Dashboard 可视化变更进度
- 社区 Schema 扩展
- Multi-Language 支持

**vs 竞品**:
- vs Spec Kit (GitHub): 更轻量、无 Python 依赖、允许自由迭代
- vs Kiro (AWS): 不锁定 IDE/模型
- vs BMAD: 有标准化规格格式

**吸收要点**: opsx 三阶段、brownfield 优先、变更级隔离、三轨互斥规格

---

### 4. garrytan/gstack v0.19 — 角色 Agent 工厂

**核心哲学**: 将 Claude Code 变成虚拟工程团队

**生产力数据**: 810× 2026 vs 2013、240× YTD、1,237 contributions、40+ features in 60 days

**23 个专业角色**:

| 阶段 | 角色 | 命令 |
|------|------|------|
| Think | YC Office Hours | `/office-hours` — 6 强制问题 |
| | CEO/Founder | `/plan-ceo-review` — 4 scope 模式 |
| | Eng Manager | `/plan-eng-review` — 数据流/状态机 |
| | Senior Designer | `/plan-design-review` — 0-10 每维度 |
| | DX Lead | `/plan-devex-review` — EXPANSION/POLISH/TRIAGE |
| Plan | Design Partner | `/design-consultation` — 完整设计系统 |
| | Design Shotgun | `/design-shotgun` — 4-6 变体比较 |
| | Autoplan | `/autoplan` — 计划快照 + 防 scope creep |
| Build | Spec-Driven Dev | `/sdd` — spec→tasks→execute |
| | Test-Driven Dev | `/tdd` — RED-GREEN-REFACTOR |
| Review | Staff Engineer | `/review` — 生产级 bug 发现 |
| | CSO | `/cso` — OWASP + STRIDE |
| | Designer | `/design-review` — AI Slop 检测 |
| | QA | `/qa-review` — 边界/回归 |
| | iOS Specialist | `/ios-review` — iOS 专用 |
| | Codex Reviewer | `/codex` — 跨模型审查 |
| Test | Browser QA | `/browser-qa` — Playwright |
| Ship | Land & Deploy | `/land` — 一键部署 |
| | Canary Monitor | `/canary` — SRE 监控 |
| Reflect | Learn | `/learn` — 模式提取 |
| Meta | Pair Agent | `/pair-agent` — 多 Agent 浏览器共享 |

**独有创新**:
- 品味记忆: 学习用户 UI 偏好，跨会话积累
- ML 注入防御三层: 22MB ML 分类器 + Canary Tokens + Haiku 转录检查
- 多 Agent 浏览器共享: `/pair-agent` — ngrok tunnel
- Sprint 流程: Think→Plan→Build→Review→Test→Ship→Reflect

**吸收要点**: 23 角色本地化、审查路由规则、品味记忆、ML 防御

---

### 5. thedotmack/claude-mem v13.4.0 — 跨会话记忆

**核心机制**: 渐进式披露 — 三层搜索 ~10x token 节省
```
search (compact index, ~50-100 tokens/条) → timeline (上下文) → get_observations (完整详情)
```

**关键特性**:
- 自动捕获: 无需手动操作（6 hooks + 15 skills）
- Web Viewer: http://localhost:37777
- 隐私控制: `<private>` 标签
- Endless Mode: 仿生记忆架构（长会话场景）
- MEMORY.md: 项目级静态索引
- 30 天置信度衰减

**吸收要点**: 渐进式披露、自动捕获、MEMORY.md↔claude-mem 统一、Chroma 向量搜索

---

## 横切基础设施

### L1 治理 — ECC v2.0 + deer-flow 2.0

#### affaan-m/ECC v2.0.0-rc.1 — 防互博 + Hook 分级

**定位**: Agent harness performance optimization system — not just configs, a complete system

**规模**:
- 15 Hook Events, 16 Hook Scripts
- 34 Rules (9 alwaysApply + 25 language-specific)
- 48 Agents (prefixed to avoid collisions)
- Skills + Commands + MCP Config

**v2.0 核心架构**:
```
Module Resolver → Target Adapter → Operation Planner → Install-State (durable)
```

**关键创新**:
1. **MANIFEST 防互博**: module conflicts 字段声明不能共存的模块
2. **Hook 分级**: `ECC_HOOK_PROFILE=minimal|standard|strict` 运行时控制
3. **选择性安装**: 按 profile/module/component 精确定制
4. **Install-State**: 持久化安装状态，支持 doctor/repair/uninstall
5. **Target Adapter**: Claude/Cursor/Antigravity/Codex/OpenCode 多目标
6. **DRY Hook Adapter**: Cursor 20 hook events → adapter.js → 复用 Claude Code hooks

**Hook 自动加载**: Claude Code v2.1+ 自动加载 plugin hooks/hooks.json — **禁止在 plugin.json 声明 hooks 字段**

**吸收要点**: MANIFEST 冲突检测、Hook 分级控制、选择性安装、Install-State

#### bytedance/deer-flow v2.0 — LangGraph 编排

**定位**: Open-source long-horizon SuperAgent harness — 70K+ stars

**技术栈**: Python 73.6% + TypeScript 15.4% | LangGraph 1.0.6+ + LangChain 1.2.3+ + FastAPI

**执行模式**:
- **flash**: 快速响应
- **standard**: 标准执行
- **pro**: 规划模式（planning）
- **ultra**: 子 Agent 并行 fan-out

**架构**:
```
Nginx → Gateway (/api/* + /api/langgraph/*) → LangGraph Server (2024)
  → Lead Agent → Middleware Chain (9 middleware) → Tools + Subagents
```

**9 层 Middleware**: ThreadData → Uploads → Sandbox → Summarization → Title → TodoList → ViewImage → Clarification

**Claude Code 集成**: `claude-to-deerflow` skill — 从 Claude Code 直接调用 DeerFlow

**核心能力**:
- Sandbox 隔离执行（Docker）
- 子 Agent 系统: max 3 concurrent, 15min timeout
- 工具: sandbox (bash/ls/read/write) + built-in + community (Tavily/Firecrawl) + MCP
- 长时记忆 + 上下文工程
- IM Channels: 支持通过消息通道交互

**吸收要点**: 执行模式概念、Claude-to-DeerFlow bridge、Sandbox 隔离、Middleware 链

---

### L2 优化 — RTK + caveman + 三级阈值

#### rtk-ai/rtk v0.42.1 — Shell Token 压缩

**效果**: 60-90% shell token 节省
**机制**: pre-rtk-rewrite hook 自动将 shell 命令重写为 rtk 代理
**元命令**: `rtk gain` (分析), `rtk discover` (发现优化机会)

#### JuliusBrussee/caveman v1.8.2 — 输出压缩

**效果**: ~75% 输出 token 节省
**模式**: lite / full / ultra / wenyan（文言文）
**触发**: 输出 >500字 / 上下文 >50% → 自动压缩

#### 三级阈值 (GSD 概念)

| 使用率 | 行动 |
|--------|------|
| <40% | 正常工作 |
| 50% | 逻辑断点 compact |
| 70% | 强制压缩或新子 Agent |

---

### L3 洞察 — codegraph + Understand-Anything + Firecrawl/Exa

#### colbymchenry/codegraph v0.9.9 — 静态代码图谱

**效果**: 47% token 减少, 58% 工具调用减少, 16% 成本降低
**MCP 工具**: search | context | trace | callers | callees | impact | node | explore | files | status
**覆盖**: 20+ 语言 + 14 框架路由 + iOS/RN 跨语言桥接
**更新**: 文件监听自动增量同步

#### Lum1104/Understand-Anything v2.7.5 — 交互知识图

**管线**: project-scanner → file-analyzer → architecture-analyzer → tour-builder → graph-reviewer → domain-analyzer
**命令**: `/understand` (分析), `/understand-chat` (问答), `/understand-dashboard` (可视化), `/understand-diff` (变更影响), `/understand-domain` (业务领域)
**团队共享**: 提交 knowledge-graph.json，队友跳过分析管线

**双引擎协同**: codegraph 查结构（静态调用链）| UA 查概念（架构/业务理解）

---

## 技能 & 最佳实践仓库

### shanraisshan/claude-code-best-practice
- lazy-load 规则系统: 按触发条件按需加载
- `<important if>` 触发模式: 条件性上下文注入
- 提示词设计: 明确角色 + 结构化输出 + Few-shot + 否定式约束

### mattpocock/skills
- **grill**: 反向推理解释器 — 从代码反推设计意图
- **triage**: 分诊模式 — P0-P3 状态机
- **共享语言**: 统一的 AI-人协作词汇表

### anthropics/skills
- SKILL.md 官方格式标准
- 技能设计指南: description 是触发器非摘要
- 官方示例: 可作为格式参考

### forrestchang/andrej-karpathy-skills
- **四原则**: Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven
- LLM 失效模式识别
- 弱命令 → 强声明式标准

### 2025Emma/vibe-coding-cn
- **道/法/术/器** 四层框架
- **α 提示词**: 唯一职责生成其他提示词
- **Ω 提示词**: 唯一职责优化其他提示词

### ComposioHQ/awesome-claude-skills
- 1000+ skills 索引目录
- 按类别组织: coding/testing/design/security/devops
- 作为发现目录使用

---

## 参考 & 工具仓库

### eyaltoledano/claude-task-master
**定位**: MCP 任务管理系统 — 27K stars
**关键创新**:
- **选择性工具加载**: all(36 tools, ~21K tokens) / standard(15, ~10K) / core(7, ~5K)
- **多编辑器支持**: Cursor/Windsurf/VS Code/Claude Code/Q CLI
- **Claude Code 集成**: `claude mcp add taskmaster-ai -- npx -y task-master-ai`
- **无需 API Key**: Claude Code CLI 模式直接使用本地实例

### x1xhlol/system-prompts-and-models-of-ai-tools
**核心发现**:
- 工具描述密度宜低不宜高（简洁描述 vs 详尽: 30% 误用减少）
- 安全护栏放入系统提示词而非工具描述
- 角色定义粒度适度（过细导致非角色场景拒绝处理）

### VoltAgent/awesome-design-md
- DESIGN.md 标准化: YAML frontmatter + Markdown
- Token 优先: 组件引用 token，不硬编码色值
- 单一来源: 项目根 DESIGN.md 为 SSOT

### ruvnet/ruflo
**定位**: Multi-agent AI harness — 100+ agents, swarm coordination
**架构**:
```
User → Ruflo (CLI/MCP) → Router → Swarm → Agents → Memory → LLM
                              ↑                          |
                              +---- Learning Loop <-------+
```
**关键特性**:
- 蜂群拓扑: hierarchical / mesh / adaptive
- HNSW 向量记忆: ~1.9x–4.7x 比 brute force 快
- SONA 自学习: 神经模式 + ReasoningBank + 轨迹学习
- 零信任联邦: 跨机器 Agent 安全协作
- 12 后台 Worker: audit/optimize/testgaps 等自动触发
- 32 Claude Code plugins + 21 npm plugins

**vs Claude Code Alone**:
| 能力 | CC Alone | + Ruflo |
|------|----------|---------|
| Agent 协作 | 隔离 | Swarm + 共享记忆 |
| 协调 | 手动 | Queen-led 层级 |
| 记忆 | 会话级 | HNSW 向量记忆 |
| 学习 | 静态 | SONA 自学习 |
| 路由 | 手动 | 89% 准确率智能路由 |

### Chalarangelo/30-seconds-of-code
- 代码片段参考库
- 按语言/框架组织
- 作为 catalog 参考，不深度集成

### hesreallyhim/awesome-claude-code
- 45.7K stars 资源索引
- 工具/技能/MCP/插件目录
- 作为外部参考

---

## CI/CD & 集成仓库

### anthropics/claude-code-action
- GitHub Action: CI/CD 中运行 Claude Code
- 适用: 自动化 PR review、代码生成、测试
- 配置: workflow YAML 中引用

### github/github-mcp-server
- GitHub API MCP 集成
- 功能: PR/Issue/Repo/Workflow 管理
- 已在 .mcp.json 中配置

### zilliztech/claude-context
- Milvus 向量数据库集成
- 启用条件: Monorepo + 已有向量索引 + 与 GSD 互补
- 按需启用，不强制

---

## 去重分析 — 功能重叠处理

| 重叠领域 | 涉及仓库 | 决策 |
|----------|----------|------|
| 任务规划 | superpowers/writing-plans vs task-master | superpowers 优先（更成熟完整） |
| Agent 编排 | superpowers/subagent vs deer-flow vs ruflo | deer-flow 做外部编排，superpowers 做内部编排，ruflo 仅概念参考 |
| 代码审查 | gstack/review vs code-review plugin | gstack 管审查流程，plugin 管 diff 检查 |
| UI 设计 | gstack/design-review vs ui-ux-pro-max | gstack 管流程，uupm 管设计库 |
| 记忆 | claude-mem vs GSD context vs claude-context | claude-mem 做主记忆，GSD 管上下文策略，claude-context 按需 |
| Shell 压缩 | RTK vs caveman | RTK 压缩输入 (shell)，caveman 压缩输出 |
| 代码探索 | codegraph vs Understand-Anything | codegraph 查结构，UA 查概念 |
| 规格 | OpenSpec vs GSD phases | OpenSpec 做功能规格，GSD phases 做多阶段规划 |

---

## 优先级排序

### 立即（本轮 /plan）
1. 整合 ECC MANIFEST 冲突检测到现有配置
2. 补全 gstack 全部 23 角色本地 agent
3. 优化 rules 触发条件（借鉴 best-practice lazy-load 模式）
4. 更新 CLAUDE.md 路由层（五柱清晰声明）

### 短期（本周）
1. 安装 OpenSpec CLI 获得 opsx 命令
2. 启用 claude-mem Chroma 向量搜索
3. 确保所有项目 codegraph init
4. 更新 sync.ps1 覆盖新 agent/rules

### 中期（本月）
1. 评估 deer-flow 作为可选外部编排引擎
2. 跟踪 ECC 2.0 正式版
3. 集成 gstack 品味记忆机制
4. opsx archive 集成到 workflow

### 长期（持续）
1. 跟踪 open-gsd/gsd-core 更新
2. 模式提取 & 持续学习
3. 社区贡献反哺

---

## 架构公式 v8

```
五柱:
  Superpowers → 方法论 (HOW): 完整开发链 + HARD-GATE
  GSD         → 上下文 (CONTEXT): 三级阈值 + 三态制品 + DAG
  OpenSpec    → 规格 (WHAT): fluid + brownfield-first + 变更隔离
  gstack      → 审查 (WHO): 23 角色虚拟团队 + 品味记忆
  claude-mem  → 记忆 (MEMORY): 渐进式披露 + 跨会话 SSOT

三横切:
  L1 治理: ECC(MANIFEST防互博+hook分级) + deer-flow(LangGraph编排)
  L2 优化: RTK(shell,60-90%) + caveman(输出,~75%) + 三级阈值(<40/50/70%)
  L3 洞察: codegraph(静态,47%减少) + UA(交互知识图) + Firecrawl/Exa(外部)

执行模式: SDD + TDD 组合 → RED-GREEN-REFACTOR → 两阶段审查 → verify
```
