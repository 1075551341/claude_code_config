# 28 仓库深度调研报告 v7.0

> 日期: 2026-06-07 | 调研方法: curl 直接获取 README + 交叉验证 | 覆盖: 全部 28 仓库

---

## 五柱骨架（企业级架构核心）

### 1. obra/superpowers — 方法论引擎（5.1.0）

**核心哲学**: 从对话开始就介入 — 不直接写代码，先问清楚要构建什么

**完整工作流链**:
```
brainstorming → using-git-worktrees → writing-plans → subagent-driven-development
→ test-driven-development → requesting-code-review → finishing-a-development-branch
```

**关键特性**:
- **HARD-GATE 设计批准**: 用户批准前禁止实现
- **两阶段审查**: spec 合规 + 代码质量，独立子 agent
- **子 agent 驱动开发**: 每个任务 fresh context，独立审查
- **TDD RED-GREEN-REFACTOR**: 写失败测试 → 看到失败 → 最小代码 → 看到通过 → 提交
- **自动技能触发**: brainstorm/plan/review 自动激活，非可选建议
- **跨平台**: Claude Code / Codex CLI / Codex App / Gemini CLI / OpenCode / Cursor / Copilot CLI
- **13 个核心 skill**: brainstorming, using-git-worktrees, writing-plans, subagent-driven-development, executing-plans, test-driven-development, requesting-code-review, receiving-code-review, finishing-a-development-branch, dispatching-parallel-agents, systematic-debugging, verification-before-completion, writing-skills, using-superpowers

**独有创新**:
- 设计文档分块展示（短到能真正阅读消化）
- 计划清晰到"热情的初级工程师都能执行"的程度
- 自主工作数小时不偏离计划

---

### 2. gsd-build/get-shit-done（已迁移至 open-gsd/gsd-core） — 上下文工程

**核心哲学**: 上下文是第一性要素 — 管理好上下文比写好代码更重要

**关键特性**:
- **三级阈值系统**: <40% 正常 / 50% compact / 70% 强制压缩
- **Read-Before-Edit 强制**: 编辑前必须 Read，防止盲目修改
- **Phase 工作流**: Minimum Viable → Core Experience → Edge Cases → Optimization
- **DAG 编排四阶段**: 拆解 → 调度 → 整合 → 验证
- **子 Agent 调度**: 无依赖并行派发，有依赖等待前置
- **制品优先加载**: openspec/ → .planning/ → memory/（而非对话历史）
- **Trust-But-Verify**: Agent 自述不可信，必须通过 API 直接验证
- **Canonical Source Precedence**: 规范文档 > ADR > 制品 > Agent 记忆

**独有创新**:
- 上下文腐烂三级阈值
- 三态制品通信（openspec + .planning + memory）
- 子 agent 间禁止通过对话历史传递状态

**注意**: 原 gsd-build/get-shit-done 已归档，重定向至 open-gsd/gsd-core

---

### 3. Fission-AI/OpenSpec — 规格格式（v1.4.1）

**核心哲学**: fluid not rigid, iterative not waterfall, built for brownfield not just greenfield

**关键特性**:
- **opsx 工作流**: `/opsx:propose` → `/opsx:apply` → `/opsx:archive`
- **每个变更独立文件夹**: proposal.md + specs/ + design.md + tasks.md
- **支持 25+ AI 工具**: Claude Code / Codex / Cursor / Windsurf / Copilot 等
- **无刚性阶段门禁**: 可随时更新任何制品
- **全局 CLI 安装**: `npm install -g @fission-ai/openspec@latest`
- **Dashboard 可视化**: 变更进度可视化
- **社区 Schema 扩展**: 类似 github/spec-kit extensions 的三方集成
- **Multi-Language 支持**: 多语言项目支持
- **brownfield 优先**: 专为已有代码库设计

**与竞品对比**:
- vs Spec Kit (GitHub): OpenSpec 更轻量、无 Python 依赖、允许自由迭代
- vs Kiro (AWS): OpenSpec 不锁定 IDE/模型
- vs nothing: 提供可预测性而无繁文缛节

**独有创新**:
- 变更级别文件夹隔离
- 归档机制保留历史上下文
- 全局 CLI + 项目级配置双层架构

---

### 4. garrytan/gstack — 角色 Agent 工厂（v0.19）

**核心哲学**: 将 Claude Code 变成虚拟工程团队 — 一个 CEO + 一个工程经理 + 一个设计师 + ...

**完整 Sprint 流程**: Think → Plan → Build → Review → Test → Ship → Reflect

**23 个专业角色**:

| 类别 | 角色 | 命令 |
|------|------|------|
| **规划** | YC Office Hours | `/office-hours` — 6 个强制问题重构产品 |
| | CEO/Founder | `/plan-ceo-review` — 4 种 scope 模式 |
| | Eng Manager | `/plan-eng-review` — ASCII 数据流/状态机 |
| | Senior Designer | `/plan-design-review` — 0-10 评分每维度 |
| | DX Lead | `/plan-devex-review` — 3 模式: EXPANSION/POLISH/TRIAGE |
| **设计** | Design Partner | `/design-consultation` — 完整设计系统 |
| | Design Explorer | `/design-shotgun` — 4-6 变体 + 品味记忆 |
| | Design Engineer | `/design-html` — Mockup→生产 HTML, 30KB 零依赖 |
| | Designer Who Codes | `/design-review` — 审计+修复+截图 |
| **开发** | Staff Engineer | `/review` — 生产级 bug 发现+自动修复 |
| | Debugger | `/investigate` — 系统根因调试, 3 次失败即停 |
| **测试** | QA Lead | `/qa` — 真浏览器测试+自动回归 |
| | QA Reporter | `/qa-only` — 纯报告模式 |
| | DX Tester | `/devex-review` — 实测 onboarding 时间 |
| **安全** | Chief Security Officer | `/cso` — OWASP + STRIDE, 17 假阳性排除 |
| **发布** | Release Engineer | `/ship` — 同步/测试/覆盖/PR |
| | Release Engineer | `/land-and-deploy` — 从 approved 到 verified |
| | SRE | `/canary` — 部署后监控循环 |
| | Performance Engineer | `/benchmark` — 前后对比 Core Web Vitals |
| **元** | Multi-Agent Coordinator | `/pair-agent` — 多 AI Agent 共享浏览器 |
| | 学习 | `/learn` — 跨会话经验提取 |

**独有创新**:
- **品味记忆**: `/design-shotgun` 学习用户偏好
- **ML 注入防御三层**: 22MB 分类器 + Canary Tokens + Haiku 转录检查
- **多 Agent 浏览器共享**: `/pair-agent` — 每个 Agent 独立 tab
- **跨 10+ AI Agent 平台**: Claude Code / Codex / OpenCode / Cursor / Factory / Slate / Kiro / Hermes / GBrain
- **Team Mode**: `--team` 自动同步到项目 `.claude/` + auto-update
- **810x 生产力**: Garry Tan 实测 2026 vs 2013 逻辑代码行

---

### 5. thedotmack/claude-mem — 跨会话记忆（v6.5.0 / plugin v13.4.0）

**核心哲学**: 渐进式披露 — 先索引后详情，~10x token 节省

**架构组件**:
1. **5 生命周期 Hooks**: SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd
2. **Worker Service**: HTTP API on port 37777 + Web Viewer UI
3. **SQLite + FTS5**: 持久化存储
4. **Chroma 向量数据库**: 混合语义+关键词搜索
5. **mem-search Skill**: 自然语言查询
6. **Smart Install**: 缓存依赖检查器

**三层搜索工作流** (~10x token 节省):
```
search (compact index, ~50-100 tokens/条)
  → timeline (时间线上下文)
    → get_observations (完整详情, ~500-1000 tokens/条)
```

**MCP 工具 (4)**:
- `search`: 全文搜索 + 类型/日期/项目过滤
- `timeline`: 时间线上下文
- `get_observations`: 批量获取详情
- `open_nodes`: 按名称打开记忆节点

**独有创新**:
- **渐进式披露**: 先过滤再取详情
- **Web Viewer**: http://localhost:37777 实时记忆流
- **`<private>` 标签**: 敏感内容排除
- **Endless Mode (Beta)**: 仿生记忆架构扩展长会话
- **30+ 语言支持**
- **OpenClaw Gateway 集成**: `curl -fsSL https://install.cmem.ai/openclaw.sh | bash`

---

## 治理与编排层

### 6. affaan-m/ECC — 治理框架（v2.0.0-rc.1）

**核心哲学**: 完整的 harness-native operator system，不只是 config

**规模**: 182K+ stars / 63 agents / 251 skills / 79 legacy commands / 12+ 语言

**关键特性**:
- **MANIFEST concern→owner→excludes**: 防 agent 互博
- **Hook 分级**: `ECC_HOOK_PROFILE=minimal|standard|strict` 运行时分级
- **选择性安装**: manifest-driven 安装管线
- **instinct-learning**: 从会话中自动提取可复用模式
- **ECC 2.0 alpha**: Rust 控制平面 + 桌面仪表盘 (Tkinter)
- **AgentShield 集成**: 安全扫描直接内嵌
- **跨 7+ harness**: Codex / Claude Code / Cursor / OpenCode / Gemini / Zed / Copilot
- **operator status snapshots**: `ecc status --markdown --write status.md` 可移植交接
- **12 语言规则**: TypeScript, Python, Go, Java, PHP, Perl, Kotlin, C++, Rust 等

**独有创新**:
- Rust 控制平面 (ECC 2.0)
- 桌面仪表盘 GUI
- 选择性安装管线
- 跨 harness 行为一致性

---

### 7. bytedance/deer-flow — LangGraph 编排（v2.0）

**核心哲学**: Super Agent Harness — 编排 sub-agents + memory + sandboxes

**关键特性**:
- **LangGraph 重写**: v2.0 完全重写，不共享 v1 代码
- **四执行模式**: flash / standard / pro / ultra (子 agent 并行 fan-out)
- **Docker Sandbox 模式**: 安全隔离执行
- **MCP Server**: deer-flow 作为 MCP server 接入
- **IM Channels**: 支持即时通讯接入
- **LangSmith/Langfuse Tracing**: 全链路追踪
- **多 LLM Provider**: OpenAI / Anthropic / OpenRouter / vLLM / Codex CLI / Claude Code OAuth
- **InfoQuest 集成**: 字节智能搜索和爬取工具
- **多模型推荐**: Doubao-Seed-2.0-Code, DeepSeek v3.2, Kimi 2.5
- **嵌入式 Python 客户端**: 可编程接口

**独有创新**:
- thinking/reasoning_effort 控制
- Codex CLI 和 Claude Code OAuth 作为 provider
- 一键 Agent 设置 (`make setup` wizard + `make doctor`)

---

## 优化工具层

### 8. rtk-ai/rtk — Shell Token 压缩（v0.42.1）

**关键特性**:
- **60-90% token 节省**: 在 dev 操作上
- **100+ 预置命令**: 覆盖常用开发操作
- **Hook 透明使用**: `git status` → `rtk git status` (0 token 开销)
- **Meta 命令**: `rtk gain` / `rtk discover` / `rtk proxy`
- **198 releases**: 活跃维护

**独有创新**:
- 透明重写（hook-based）
- 用量分析 (`rtk gain --history`)

---

### 9. JuliusBrussee/caveman — 输出压缩（v1.8.2）

**关键特性**:
- **四模式**: lite / full / ultra / wenyan (文言文)
- **仅压缩输出**: 输入不压缩，保留上下文忠实度
- **学术佐证**: 基于 LLM 压缩研究
- **~75% 输出 token 节省**

**独有创新**:
- 文言文压缩模式
- 四级渐进压缩

---

### 10. colbymchenry/codegraph — 静态代码图谱（v0.9.9）

**核心哲学**: 给 Explore Agent 一个预索引的知识图谱，而非每次扫描文件

**基准测试结果** (7 仓库, 7 语言, Opus 4.8):
| 指标 | 节省 |
|------|------|
| Token | **47% 减少** |
| 工具调用 | **58% 减少** |
| 成本 | **16% 降低** |
| 时间 | **22% 更快** |

**关键特性**:
- **20+ 语言支持**: TypeScript/JS, Python, Go, Rust, Java, C#, PHP, Ruby, C, C++, ObjC, Swift, Kotlin, Dart, Lua, Svelte, Liquid, Pascal
- **14 框架路由识别**: Django/Flask/FastAPI/Express/NestJS/Laravel/Drupal/Rails/Spring/Gin/Axum/ASP.NET/Vapor/React Router/SvelteKit
- **跨语言桥接 iOS/RN/Expo**: Swift↔ObjC, RN legacy bridge + TurboModules, Fabric view, Expo Modules
- **100% 本地**: 无数据离开本机，SQLite only
- **文件监听自动同步**: FSEvents/inotify/ReadDirectoryChangesW + 防抖
- **staleness banner**: 编辑后未同步期间明确警告 agent
- **MCP 工具 (10+)**: codegraph_search, context, trace, callers, callees, impact, node, explore, files, status
- **Connect-time catch-up**: 重连时自动增量同步

**独有创新**:
- 框架路由→handler 链接（URL pattern → handler function）
- 跨语言桥接（静态解析做不到的）
- 文件 staleness 标记机制

---

### 11. Lum1104/Understand-Anything — 交互知识图（v2.7.3）

**关键特性**:
- **多 Agent 管线**: project-scanner → file-analyzer → architecture-analyzer → tour-builder → graph-reviewer → domain-analyzer
- **9 个命令**: understand, chat, dashboard, diff, domain, explain, knowledge, onboard, onboard
- **跨 8+ 平台**: Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, Vibe CLI, Trae
- **团队共享**: 提交 `.understand-anything/knowledge-graph.json`，队友跳过分析
- **增量更新**: `--auto-update` 通过 post-commit hook 自动补丁
- **Discord 社区**: 活跃支持

**与 CodeGraph 互补**:
| 场景 | CodeGraph | UA |
|------|-----------|-----|
| 代码结构/调用链 | ✅ 首选 | — |
| 概念理解/架构导览 | — | ✅ 首选 |
| 探索未知代码 | 查结构 | 查概念 |

---

### 12. github/github-mcp-server — GitHub 集成

**关键特性**:
- **16+ toolsets**: issue, PR, repository, search, workflow, organization 等
- **Lockdown 模式**: 精细权限控制
- **Enterprise 兼容**: GitHub Enterprise Server 支持
- **官方维护**: github.com/github 组织

---

### 13. anthropics/claude-code-action — CI/CD 集成（v1.0）

**关键特性**:
- **4 云后端**: 支持 AWS / GCP / Azure / 自有
- **智能模式检测**: 自动识别任务类型
- **结构化 JSON 输出**: CI 友好
- **Issue/PR 触发**: GitHub Actions 事件驱动

---

### 14. zilliztech/claude-context — 向量上下文

**关键特性**:
- **BM25 + 稠密混合搜索**: 语义 + 关键词双路
- **~40% token 节省**: 只检索相关上下文
- **Milvus 向量数据库**: 高性能
- **210 commits**: 活跃开发

---

## 技能与最佳实践

### 15. anthropics/skills — 官方 Skill 标准

**关键特性**:
- **Formal SKILL.md spec**: YAML frontmatter (name + description) + Markdown 指令
- **三平台**: Claude Code / Claude.ai / Claude API
- **技能类型**: Creative & Design / Development & Technical / Enterprise & Communication / Document Skills
- **渐进披露**: 文件夹格式 (progressive disclosure)
- **plugin marketplace 集成**: `/plugin marketplace add anthropics/skills`
- **agentskills.io**: 开放标准

**核心格式**:
```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name
[Instructions here]
## Examples | Guidelines
```

---

### 16. shanraisshan/claude-code-best-practice — 最佳实践（v2.1.162）

**关键特性**:
- **80+ 提示词模板**: 覆盖所有开发场景
- **10+ 方法论**: 系统化开发流程
- **lazy-load 规则系统**: `paths: glob` 按文件类型加载
- **`<important if>` 条件触发**: 上下文感知规则激活
- **编排模式**: Research → Plan → Execute → Review → Ship

---

### 17. mattpocock/skills — 实战工程师技能

**核心哲学**: "for real engineers — not vibe coding"

**关键技能**:
- **`/grill-me`**: 反推式提问，消除沟通鸿沟
- **`/grill-with-docs`**: 同上 + 构建共享语言 + ADR
- **`/triage`**: P0-P3 状态机分诊
- **`/improve-codebase-architecture`**: 代码库架构改进
- **共享语言模式**: 帮助 Agent 解码项目术语，减少 token 消耗
- **CONTEXT.md 生成**: 项目上下文文档

**独有创新**:
- "共享语言" 概念 — 比代码更省 token
- grill 反推方法论
- skills.sh 安装器

---

### 18. forrestchang/andrej-karpathy-skills — Karpathy 四原则

**核心四原则**:
1. **Think Before Coding** — 先陈述假设
2. **Simplicity First** — 能 50 行不写 200 行
3. **Surgical Changes** — 只改必须改的
4. **Goal-Driven** — 弱命令转强声明式

**独有创新**:
- LLM 失效模式对策
- 系统提示词中的 Karpathy 哲学编码

---

### 19. 2025Emma/vibe-coding-cn — 道法术器框架

**核心框架**:
```
道(原则): AI能做的不人工做 | 先结构后代码 | 上下文是第一性要素
法(策略): 接口先行实现后补 | 能抄不写 | 文档即上下文
术(技巧): 明确能改什么不能改什么 | Debug给预期vs实际+最小复现
器(工具): Claude Code/Cursor/Codex CLI — 选最合适的
```

**独有创新**:
- **α-提示词(生成器)**: 唯一职责生成其他提示词
- **Ω-提示词(优化器)**: 唯一职责优化其他提示词
- 中文原生设计哲学

---

### 20. Chalarangelo/30-seconds-of-code — 代码片段库（v14.0.0）

**关键特性**:
- **多语言**: JavaScript 65.4% + Python + CSS + React + Git 等
- **简洁片段**: 每个 <30 秒理解
- **最佳实践编码**: 可作为 reference/catalog

---

### 21. x1xhlol/system-prompts-and-models-of-ai-tools — 系统提示词对比

**关键特性**:
- **30+ 工具提示词比较**: Cursor/Windsurf/Devin/Claude Code 等
- **注入防护**: ZeroLeaks 服务
- **实证发现**:
  - 工具描述密度宜低不宜高（减少 30% 误用）
  - 安全护栏放入系统提示词而非工具描述
  - 角色定义粒度适度

---

## 设计与参考索引

### 22. eyaltoledano/claude-task-master — 任务管理（v0.43.1）

**关键特性**:
- **MCP 协议**: 标准 MCP server
- **3 级工具裁剪**: 按任务复杂度调整可用工具
- **PRD→结构化任务**: 从 PRD 自动分解任务

---

### 23. VoltAgent/awesome-design-md — 设计系统规范

**关键特性**:
- **72 个 DESIGN.md 示例**: 来自知名品牌
- **9 节推荐结构**: colors, typography, spacing, motion 等
- **YAML frontmatter + Markdown**: machine + human readable
- **零依赖**: 纯规范文件

---

### 24. nextlevelbuilder/ui-ux-pro-max-skill — UI/UX 设计智能（v2.0）

**关键特性**:
- **67 UI 风格** + **161 色板** + **57 字体配对** + **25 图表类型**
- **161 行业推理规则**: 每个行业有推荐 pattern/style/color/typography/effects + 反模式
- **15 技术栈支持**: React, Next.js, Vue, Svelte, SwiftUI, Flutter 等
- **99 UX 指南**: 最佳实践 + 反模式 + 无障碍规则
- **99 UX 指南**
- **设计系统生成器**: AI 推理引擎自动生成完整设计系统
- **npm CLI**: `uipro-cli`

---

### 25. ComposioHQ/awesome-claude-skills — 技能索引

**关键特性**:
- **1000+ skills 索引**: 分类整理
- **渐进式加载模式**: 按需加载技能
- **社区驱动**: 持续增长

---

### 26. hesreallyhim/awesome-claude-code — Claude Code 资源

**关键特性**:
- **45.7k stars**: 最大 Claude Code 资源索引
- **配置范式**: 最佳实践配置示例
- **工具发现**: 生态工具目录
- **重构中**: 正在重新组织

---

### 27. ruvnet/ruflo — 蜂群拓扑（v3.10.34）

**关键特性**:
- **HNSW 向量记忆**: ~1.9x 更快
- **3 共识算法**: Raft / Byzantine / Gossip
- **100+ agents 蜂群拓扑**: 大规模并行
- **1524 releases**: 极度活跃
- **3-Tier Model Routing**: 智能模型路由

**概念吸收**: 蜂群模式适合多团队协作，单用户由 agentic-orchestrator 覆盖

---

## 架构公式 v7.0

```
五柱(纵向阶段驱动) × 五阶段(流程) × 三横切(基础设施)

五柱:
  Superpowers → 方法论 (13 skill 链 + HARD-GATE + 双阶段审查)
  GSD         → 上下文工程 (三级阈值 + DAG 编排 + 三态制品)
  OpenSpec    → 规格格式 (opsx 工作流 + brownfield 优先 + 25 工具)
  gstack      → 角色 Agent (23 角色 + Sprint 流程 + ML 防御)
  claude-mem  → 跨会话记忆 (渐进式披露 + 3 层搜索 + 10x token 节省)

三横切:
  L1 治理 — ECC(MANIFEST 防互博+hook 分级) + deer-flow 2.0(LangGraph 编排)
  L2 优化 — RTK(shell, 60-90%) + caveman(输出, ~75%) + 三级阈值
  L3 洞察 — codegraph(47% token 减少) + Understand-Anything(知识图) + Firecrawl/Exa

核心改进(v6→v7):
  ① gstack v0.19: +ML注入防御 +品味记忆 +多Agent浏览器共享
  ② ECC v2.0.0-rc.1: +Rust控制平面 +桌面仪表盘 +选择性安装
  ③ claude-mem v6.5.0: +Chroma向量 +Endless Mode +OpenClaw Gateway
  ④ deer-flow v2.0: +LangGraph重写 +4执行模式 +Docker沙箱
  ⑤ codegraph v0.9.9: +staleness banner +connect-time catch-up +Opus 4.8基准
  ⑥ OpenSpec v1.4.1: +opsx工作流 +25+工具 +Dashboard
  ⑦ mattpocock/skills: +共享语言 +grill反推 +triage分诊
  ⑧ UI UX Pro Max v2.0: +设计系统生成器 +161推理规则
```

## 规模约束 v7.0

| 类型 | v6.0 | v7.0 建议 | 变化 |
|------|------|-----------|------|
| skills | 28 | 28-30 | +gstack 集成 |
| agents | 22 | 25 | +gstack 角色细化 |
| rules | 10 | 10 | 内容优化 |
| hooks | 16 | 16 | claude-mem 升级 |
| CLAUDE.md | ~202行 | ~200行 | 精炼 |
| MCP servers | 18 | 20 | codegraph+UA 强化 |

## 关联文档

- 本报告: `docs/research/28-repo-deep-research-v7.md`
- 五柱详解: `docs/research/five-pillars-v7.md`
- 设计文档: `spec/claude-config-integration/design-v7.md`
- 实施计划: 下一步 `/plan` 产出
