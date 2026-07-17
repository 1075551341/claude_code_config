# thedotmack/claude-mem v13.8.1

> 层: 五柱核心(L3横切) | 置信度: 高 | 刷新: 2026-06-26 | Stars: 82.8K+ | License: Apache-2.0

## v10.5 delta (2026-07-17)

- **最新元数据**：87,521 stars；GitHub Release **v13.11.0**；`pushed_at` 2026-07-16T11:34:41Z。
- **自 2026-06-29 的变化**：从 v13.8.1 升至 v13.11.0；已确认版本推进，但本轮未发现足以改变 R18、三层检索或 Endless Mode 默认关闭的证据。
- **本地吸收**：不变——claude-mem 继续是跨会话记忆 SSOT；不以版本漂移替换 codegraph/cbm 的结构职责。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有 npm 研究记录。


## v10.5.1 delta (2026-07-17)
- **最新元数据**：87,527★；Release **v13.11.0**（2026-07-13）；`pushed_at` 2026-07-16T11:34:41Z。
- **漂移要点**：Worker-native cloud sync（退役独立 `cloud-sync.mjs`）；`/cloud-sync` skill；schema v40 自修复；prompt↔session 映射修复。
- **本地吸收 / 缺口**：钉 **13.8.x**；升 13.11 待评估。已有：R18 search→observations、记忆柱。
- **不吸收**：cmem.ai 云同步默认开启（隐私/企业边界需单独评估）。
- **双源**：GitHub API + Firecrawl（v13.11.0 release）。
## 核心价值

claude-mem 是 Alex Newman (@thedotmack) 构建的持久记忆压缩系统，为 Claude Code 等 AI coding agent 提供跨会话长期记忆层。自动捕获工具调用观察、AI压缩为结构化摘要、注入未来会话上下文 -- 解决 agent 每次启动从零开始 的核心痛点。

**五柱定位**：归属 MANIFEST concern memory + context_retrieval，是 R18（记忆优先）的 SSOT 实现引擎。在 v10.1 架构中属于 L3 横切洞察层，与 codegraph（代码探索）互补。

### 核心优势总览

| 维度 | 能力 | 量化 |
|------|------|------|
| Token 节省 | 三层渐进式检索 | ~10x vs 全量注入 |
| 跨会话 | 自动捕获 -> 压缩 -> 注入 | 零手动管理 |
| 代码探索 | tree-sitter AST 结构搜索 | 4-55x vs Read/Explore agent |
| 知识构建 | Corpus 知识库 + Agent SDK 问答 | 从原始观察到可查询大脑 |
| 架构治理 | Pathfinder 流程图表 + 去重 | 4阶段 feature->unify->handoff |
| 隐私 | <private> 标签过滤 + 本地存储 | 零外部 API 调用（可配） |
| 可扩展 | Server Beta (Postgres + Redis) | 单机 -> 多租户伸缩 |

---

## 三层检索（Progressive Disclosure）

claude-mem 的核心 token 优化策略：**先过滤，后获取**。三层依次递进，每层仅在确认相关性后才进入下一层。

### 层架构



### Layer 1 -- search(query, limit, project, type, obs_type, dateStart, dateEnd, orderBy)

- 返回紧凑索引表格：ID + 标题 + 时间戳 + 类型图标
- 图标系统：critical / decision / informational / feature / bugfix
- SearchManager.ts 负责参数标准化 + 策略路由
- 无 query text -> 直接 SQLite 过滤；有 query -> Chroma 向量搜索

### Layer 2 -- timeline(anchor, query, depth_before, depth_after, project)

- 锚点类型：Observation ID 精确锚定 / query 语义自动查找
- 交叉排列 observations + sessions + user prompts 按时间序
- TimelineService.ts 计算窗口切片、按日期分组
- 用途：理解事件发生的上下文序列，而不只是知道匹配了什么

### Layer 3 -- get_observations(ids, orderBy, limit, project)

- 批量获取完整 observation 对象（narrative + facts + concepts + files）
- 设计为 2+ IDs 批量调用以节省 token 和延迟
- 仅在 Layer 1+2 确认相关后才调用

### Token 节省量化

| 方式 | 20 条结果 | 效率 |
|------|----------|------|
| 全量获取（naive） | ~15,000 tokens | 基线 |
| 纯索引（Layer 1） | ~1,500 tokens | **10x 节省** |
| 索引 + 选择性获取 | ~3,000 tokens | **5x 节省** |

### 路由策略

| 查询类型 | 引擎 | 退化策略 |
|----------|------|---------|
| 纯过滤器（日期/类型/项目） | SQLite 直查 | -- |
| 语义查询（自然语言） | ChromaDB 向量 -> 取 ID -> SQLite 水合 | Chroma 不可用 -> FTS5 关键词 |
| 混合（语义 + 元数据过滤） | ChromaDB 结果 JOIN SQLite 过滤 | 同上 |

---

## 技能矩阵（15 Skills，v13.3+）

| 技能 | 引入版本 | 用途 | 触发场景 |
|------|---------|------|---------|
| mem-search | v4 | 渐进式三层检索历史记忆 | 上次怎么解决的？ |
| smart-explore | v12 | tree-sitter AST 结构代码探索 | 替代 Glob->Grep->Read |
| knowledge-agent | v12.1 | 构建 AI 知识库 + 会话问答 | 从观察历史编译专题大脑 |
| pathfinder | v13.0 | 代码库 -> 特性分组流程图 + 去重 | 重构前审计架构 |
| timeline-report | v12 | 项目完整开发历史叙事报告 | 给这个项目写历史 |
| weekly-digests | v13.3 | 按 ISO 周拆分系列章节 | 周报、按周拆解 |
| make-plan | v10 | 详细分阶段实施计划 + 文档发现 | 执行前规划 |
| do | v10 | 执行分阶段实施计划（子Agent） | 执行 plan |
| babysit | v11 | 监控 PR/审查周期直到可合并 | 盯着这个 PR |
| how-it-works | v11 | 解释 claude-mem 内部机制 | claude-mem 怎么工作？ |
| learn-codebase | v11 | 通读所有源文件预处理项目 | 学习这个代码库 |
| standup | v12 | 跨 worktree/分支只读 standup | 多分支变更对比 |
| oh-my-issues | v13.3 | 根因聚类 issue 积压 | 合并重复 issues |
| design-is | v13.3 | Dieter Rams 十原则设计审计 | 审查这个 UI |
| version-bump | v12 | 自动化语义版本 + npm 发布 | 发版 |
| wowerpoint | v13.2 | 文档 -> 幻灯片 PDF | 把这个做成 slides |

### 重点技能详解

#### knowledge-agent（v12.1+）

6 个 MCP 工具：build_corpus / list_corpora / prime_corpus / query_corpus / rebuild_corpus / reprime_corpus

- **CorpusBuilder** -- 搜索 observations -> 水合完整记录 -> 持久化到 ~/.claude-mem/corpora/
- **CorpusRenderer** -- 渲染为全详情 prompt 文本（支持 1M token 上下文窗口）
- **KnowledgeAgent** -- 管理 Agent SDK 会话，支持会话恢复多轮问答
- **Auto-reprime** -- 过期会话自动重新 prime 并重试

#### smart-explore（v12.0+）

tree-sitter AST 解析，支持 24 种语言（TypeScript, JavaScript, Python, Rust, Go, Java, C, C++, C#, Ruby, PHP, Swift, Kotlin, Scala, Bash, CSS, SCSS, HTML, Lua, Haskell, Elixir, Zig, TOML, YAML）。核心原则：先索引，后按需获取。

| 工具 | Token 消耗 | 用途 |
|------|-----------|------|
| smart_search | ~2,000-6,000 | 跨目录发现文件+符号，单次调用 |
| smart_outline | ~1,000-2,000 | 单文件结构骨架（所有函数/类/方法签名） |
| smart_unfold | ~400-2,100 | 展开指定符号完整源码（含 JSDoc/装饰器） |

**Token 节省对比**：

| 场景 | smart-explore | 传统方式 | 节省倍数 |
|------|-------------|---------|---------|
| 理解单文件 | ~3,000 (outline+unfold) | ~12,000 (Read全文) | **4-8x** |
| 探索代码库 | ~3,000-8,000 | ~39,000-59,000 (Explore agent) | **11-18x** |
| 读 27 行函数 | ~400 (unfold) | ~22,000 (Explore agent) | **55x** |

#### pathfinder（v13.0+）

4 阶段将代码库映射为特性分组流程图，识别重复，提出统一架构方案：

| 阶段 | 内容 | 产出 |
|------|------|------|
| Phase 0: Feature Discovery | 遍历源码树，基于目录+import 提议特性边界 | 00-features.md |
| Phase 1: Per-Feature Flowcharts | 每特性一个子 Agent 追踪 happy paths + 副作用 | 01-flowcharts/feature.md (Mermaid) |
| Phase 2: Duplication Hunt | 特性内+跨特性重复检测，每声明附 file:line | 02-duplication-report.md |
| Phase 3: Unified Proposal | 最简统一设计（禁止抽象层/feature flag） | 03-unified-proposal.md + Mermaid 总图 |
| Phase 4: Handoff Prompts | 每系统 /make-plan prompt，含确切调用点 | 04-handoff-prompts.md |

原则：证据优先（每节点附 file:line）| 当前状态先于理想状态 | 最简统一（宁删勿抽象）| 只到 handoff 不实现

#### timeline-report / weekly-digests（v12/v13.3）

- **timeline-report**：单次生成 Journey Into [Project] 叙事报告，分析完整开发历史
- **weekly-digests**：将完整时间线拆分为 ISO 周文件，每前一周的 carry-forward block 传给下一子 Agent，生成序列章节

---

## 存储架构

### 双数据库策略

| 维度 | SQLite | ChromaDB |
|------|--------|----------|
| 角色 | **权威数据源** (SSOT) | 向量语义索引 |
| 保证 | ACID + 外键 CASCADE | 最终一致性 |
| 查询 | 结构化过滤（日期/类型/项目） | 语义相似度搜索 |
| 可重建 | -- | 可从 SQLite Backfill |
| 去重 | content_hash 唯一约束 | -- |
| 迁移 | MigrationRunner 幂等版本追踪 | Watermark 增量同步 |

### ChromaDB 细节

- Collection 命名：cm__ + sanitized project name
- 文档分解：一条 SQLite observation -> 多个 Chroma 文档（narrative / text / individual facts）
- 目的：提高检索粒度，不同语义片段独立匹配
- 同步：ChromaSync.ensureConnection() 管理连接生命周期

### 关键优化

- **WAL 模式** -- SQLite 高并发读写（DatabaseManager 初始化 PRAGMA）
- **Claim-Confirm 模式** -- pending messages 先 claim 再 confirm，防数据丢失
- **JSON 列** -- facts / concepts 以 JSON 字符串存储灵活字段
- **Session ID 双态**：content_session_id（稳定对外ID） vs memory_session_id（内部 agent 特定 ID）

### 数据流

Hook 捕获工具输出 -> SessionMessageBuffer(异步队列)
  -> Worker 消费 -> AI Provider(Claude/Gemini/OpenRouter) 压缩
  -> ResponseProcessor 解析 XML -> 写入 SQLite + ChromaDB
  -> SessionStart 时 ContextBuilder 生成 MEMORY.md/CLAUDE.md 注入新会话

---

## 跨会话记忆

### 5 生命周期 Hooks（全自动）

| Hook | 触发点 | 职责 |
|------|--------|------|
| **SessionStart** | startup / clear / compact | 启动 Worker + 生成 MEMORY.md 上下文 |
| **UserPromptSubmit** | 每次用户输入 | 追踪 prompt 历史 + 初始化会话状态 |
| **PostToolUse** | 每次工具执行后 | 队列化工具输出异步 observation 提取 |
| **PreToolUse** | Read 工具前 | 注入特定文件上下文到 prompt |
| **Stop** | 会话中断/暂停 | 最终化会话 + 触发摘要生成 |

### 上下文注入机制

ContextBuilder.ts 的 generateContext 函数在三种场景触发：

1. **会话初始化** -- context-generator.cjs 在 SessionStart 时获取上下文
2. **按需 API** -- /api/context/inject + /api/context/preview 动态检索
3. **跨项目** -- 同时查询多项目 observations 和 summaries

### Token 经济学

| 指标 | 含义 |
|------|------|
| **Read Tokens** | 注入记忆到当前会话的估算成本 |
| **Work Tokens** | AI 原始执行该工作的 token 成本 |
| **Savings %** | 通过回忆避免重做节省的 token 百分比 |

### 平台隔离

所有引擎写入同一 SQLite 数据库，通过 platform_source 字段标记：

| 引擎 | platform_source |
|------|----------------|
| Claude Code | claude |
| Codex CLI | codex |
| OpenClaw | openclaw |
| Gemini CLI | gemini |
| Cursor | cursor |
| Pi-Agent | pi-agent |

平台间完全命名空间隔离，搜索结果可按来源过滤。

### MEMORY.md <-> claude-mem 统一方案

- **Auto-generated folder-level CLAUDE.md** -- 每个目录生成含开发活动时间线的 CLAUDE.md
- **claude-mem-context 标签包裹** -- 自动生成内容被特殊标签包裹，保护用户手动内容，防止递归观测
- **Project Root Protection** -- 含 .git 的目录排除自动更新，根 CLAUDE.md 保持用户管理
- **Worktree Support** -- 检测 git worktree，父仓库 + worktree 交叉时间线
- **Configurable** -- CLAUDE_MEM_CONTEXT_OBSERVATIONS（默认 50）控制注入条数

### Endless Mode（Beta，实验性）

受生物记忆启发的两层架构：

| 层 | 存储 | 特性 |
|----|------|------|
| **Working Memory** (上下文窗口) | 仅压缩 observations（~500 tokens/条） | 快速、高效 |
| **Archive Memory** (Transcript 文件) | 完整工具输出保留在磁盘 | 完美回忆、可搜索 |

**PostToolUse 阻塞机制**：每次工具调用后等待 Worker 生成压缩 observation -> 转换 transcript 文件 -> 完整工具输出替换为压缩版 -> Claude 以压缩上下文继续。目标是 O(N^2) -> O(N) 线性增长。

**当前状态**（v10.1 评估结论维持）：
- 实验性，默认关闭；生产稳定性未经验证
- 每次工具调用增加延迟（阻塞等待压缩）
- 效率数据基于理论建模非生产实测
- .claude 配置策略：**压缩 + R18 + GSD 70% 断点**替代 Endless Mode

---

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| memory / context_retrieval | installed_plugins.json -> claude-mem plugin + skills/claude-mem-maintenance/SKILL.md |
| R18 记忆优先 | rules/CORE.md R17-R18工具路由, rules/CONTEXT.md claude-mem三层搜索 |
| 渐进式检索规范 | rules/CONTEXT.md claude-mem三层搜索工作流 |
| Endless Mode 决策 | docs/ADR/2026-06-16-v10-ua-disabled-endless-mode.md Section 2 |
| 技能加载 | L4 显式调用：mem-search / smart-explore / knowledge-agent / timeline-report |
| 数据存储 | ~/.claude-mem/claude-mem.db (SQLite) + ~/.claude-mem/chroma/ (ChromaDB) |

---

## 吸收建议

### 采纳

1. **claude-mem 为 SSOT** -- 跨会话记忆唯一权威源；claude-mem search 优先于重复文件分析（R18）
2. **三层渐进式检索** -- 已文档化于 CONTEXT.md，每次使用 search -> timeline -> get_observations 流程
3. **smart-explore 与 codegraph 协同**：
   - smart-explore：AST 结构代码探索（token 高效读源码）
   - codegraph：预索引知识图谱（符号级调用链/影响分析）
   - 互补非替代：smart-explore 用于文件级结构探索，codegraph 用于符号级关系查询
4. **knowledge-agent** -- 重要项目编译知识库，定期更新
5. **timeline-report + weekly-digests** -- 大项目结束/里程碑时生成叙事报告
6. **pathfinder** -- 重构前必跑，识别重复和统一机会

### 不采纳/有条件

1. **Endless Mode** -- **默认关闭**。当前 claude-mem 已足够；Endless 增加延迟且未生产验证。用压缩 + R18 + GSD 70% 断点取得同等效果
2. **Server Beta** -- 当前不需要多租户/Postgres 伸缩；单机 SQLite 足够
3. **claude-context (zilliztech)** -- v10.4 **archived_redirect** → codebase-memory-mcp；见 [deusdata-codebase-memory-mcp](deusdata-codebase-memory-mcp.md)

### 版本策略

- 主版本锁定：v13.x（非用户要求不升 major，R14）
- 更新命令：npx claude-mem install（非 npm install -g，后者仅安装 SDK 不注册 hooks）

---

## 互博检查

### vs codebase-memory-mcp / claude-context（v10.4）

| 维度 | claude-mem | codebase-memory-mcp | claude-context（已归档） |
|------|------------|---------------------|--------------------------|
| **核心问题** | 跨会话记忆 | 代码结构图/ADR/架构 | 向量代码搜索（Milvus） |
| **存储** | SQLite + ChromaDB | 本地知识图谱 | Milvus |
| **与 mem 关系** | SSOT 记忆 | 互补，不替代 R18 | archived_redirect→cbm |

**决策**：
- **claude-mem SSOT** -- 跨会话记忆唯一权威源
- **codebase-memory L4 按需** -- 架构/ADR/变更；替代 claude-context 语义搜索位
- **两者不冲突** -- claude-mem 管"做了什么"，cbm 管"代码结构在哪"

### vs agent/context-manager

- agent/context-manager **已合并至 claude-mem** -- 禁止恢复
- claude-mem 的 search->timeline->get_observations 替代原有 context-manager 功能

### vs Claude Code 原生 auto-memory

| 维度 | claude-mem | Claude Code 原生 |
|------|-----------|-----------------|
| 触发 | 5 生命周期 Hook 全自动 | 会话结束 auto-memory |
| 检索 | 三层渐进式 + 语义搜索 | 全文件加载（无搜索） |
| Token | ~10x 节省 | 随文件线性增长 |
| 跨平台 | 6+ 引擎 | 仅 Claude Code |

### vs claude-mem-lite

- claude-mem-lite 是 claude-mem 的精简重写：Haiku 替代 Sonnet（~600x 成本降低）、仅 3 个 npm 包、按需生成退出
- **当前不切换**：claude-mem v13.6.1 生产稳定，82.8K stars 社区验证充分
- 如 token 成本成为瓶颈可评估

---

## v13 最新动态

### v13.6.1 (2026-06-15) -- 当前版本
- Telemetry 回填经济学：将推断的生成成本经济学回填到匿名每日 telemetry rollups
- Scrub 覆盖 + 测试

### v13.5.x 系列 (2026-06-10~13) -- Telemetry 基础设施
- v13.5.0：首个 telemetry 版本 -- PostHog 匿名分析，严格白名单洗涤，npx claude-mem telemetry disable 可退出
- v13.5.1-5.5：token 经济学信号、GeoIP 修复（98.5% 未知位置 gap -> 0）、可靠性信号（搜索质量/压缩信任度/Worker 生命周期/hook 失败/内存健康）
- v13.5.6：Worker 重启架构重写 -- 消除 ping-pong 风暴和 EADDRINUSE；自替换 Worker 模型；2247 测试通过
- v13.5.7：过期 CLI 二进制解析修复 -- 探测能力而非仅检查存在；缓存成功 15 分钟，失败不缓存

### v13.4.x 系列 (2026-05-29~06-09)
- v13.4.0：清空大规模缺陷积压（plans 01-11）；OpenRouter 提供商可配 base URL；测试 46->0 失败，typecheck 24->0 错误
- v13.4.1-4.2：可选交互式邮件 opt-in（npx claude-mem install 时收集 work email）

### v13.3.0 (2026-05-21)
- 新增 3 个技能：design-is / weekly-digests / oh-my-issues
- 修复重复 .mcp.json 警告；停止 Codex transcript 重放

### v13.0.0~v13.2.0 (2026-05-08~12)
- v13.0.0：Server Beta（Postgres + BullMQ + Redis）+ AGPL->Apache 2.0 重新许可
- v13.1.0：完整 server-beta 事件管线（4-13 阶段）+ 3 AI 提供商 + Docker Compose
- v13.2.0：wowerpoint 技能，达到 12 skills 总数

---

## 证据

- 本地 installed_plugins.json 实测 v13.6.1
- [GitHub thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) -- 82.8K+ stars, 7.2K+ forks
- [官方文档 docs.claude-mem.ai](https://docs.claude-mem.ai/)
- [DeepWiki 架构分析](https://deepwiki.com/thedotmack/claude-mem)
- [memsearch 对比页面](https://zilliztech.github.io/memsearch/home/comparison/)
- [claude-mem 中文深入解读](https://zwt0204.github.io/github/2026/04/16/claude-mem-deep-dive/)

---

## v10.1 增量

- Endless Mode 评估结论维持：压缩 + R18 + GSD 70% 断点替代；默认关闭
- 三层检索文档化于 CONTEXT.md -- 无 upstream breaking
- smart-explore 与 codegraph 协同策略明确：文件级 vs 符号级
- knowledge-agent + pathfinder 纳入重构前必跑流程
- v13 完整版本历程补充（13.0.0 -> 13.6.1）

## v10.3.1 增量（三源刷新 2026-06-26）

**v13.6.1 → v13.8.1**（npm registry + GitHub package.json + GitHub Releases 三源交叉验证）：
- npm `claude-mem@13.8.1` 为最新稳定版（registry.npmjs.org/claude-mem/latest 确认）
- GitHub Releases 页面**不完整**：仅显示至 v13.3.0 (2026-05-21)，v13.4+ 仅 npm 发布未创建 release notes
- GitHub `package.json` version 字段 = "13.8.1"（双源确认）
- 卡片原 v13.6.1 (2026-06-15) 已被 v13.8.1 超越

**版本纠正说明**：
- 卡片标题 v13.6.1 → v13.8.1（同步 npm 上游最新版本）
- **本地实际安装版本**: v13.6.0（installed_plugins.json 实测，lastUpdated: 2026-06-13）
- **本地缓存目录**: plugins/cache/thedotmack/claude-mem/ 含 13.5.6/13.6.0/13.6.2 三个版本，最高 13.6.2（未注册安装）
- 上游 vs 本地差异: v13.8.1（npm）vs v13.6.0（本地），差 2 个 minor 版本
- 升级路径: `npx claude-mem install`（非 npm install -g，后者仅装 SDK 不注册 hooks）

**本地影响**：
- MANIFEST concern `memory` 路径不变（installed_plugins.json + skills/claude-mem-maintenance/SKILL.md）
- R14 锁定 major v13.x 维持（v13 → v14 需用户确认）
- R18 记忆优先策略不变（三层检索 search → timeline → get_observations）
- 升级路径：`npx claude-mem install`（非 npm install -g，后者仅装 SDK 不注册 hooks）

## v10.4 增量（2026-06-29）

- 上游无新版本（npm 仍 v13.8.1）；R18 SSOT 决策不变
- vs codebase-memory-mcp：mem=跨会话记忆；cbm=代码结构图，边界已在 [deusdata-codebase-memory-mcp](deusdata-codebase-memory-mcp.md) 声明