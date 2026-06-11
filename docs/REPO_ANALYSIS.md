# 仓库全量分析报告

> 版本 v1.0 | 分析范围: 28个仓库 | 目标: .claude 配置融合优化

---

## 一、核心骨架（五柱）评估

### 1. superpowers（方法论骨架）⭐⭐⭐⭐⭐
**仓库**: `obra/superpowers` | Stars: 213K | 官方插件市场支持

**核心优势**:
- 完整 SDD + TDD 组合工作流，Socratic 设计精炼
- 强制 RED-GREEN-REFACTOR 循环，防止无测试开发
- subagent-driven-development：两阶段审查（spec合规→代码质量）+ 不问"继续"连续执行
- 技能发现路由系统（using-superpowers）
- SessionStart bootstrap：会话开始自动加载
- 技能命名规范：SKILL.md frontmatter，always/lazy分级

**已有且可复用**:
- 13个技能名称与本地完全对齐（brainstorming/writing-plans/executing-plans等）
- 后加载覆盖原则已设计好：本地覆盖插件
- 实际内容差距：本地版本为精简覆盖，保留了token效率优势

**待补强**:
- v5.1.0 新增: writing-skills meta-skill（TDD应用于技能文档本身）→ 已有但需校验
- dispatching-parallel-agents 并行工作流 → 本地 agentic-orchestrator agent 覆盖

---

### 2. get-shit-done/GSD（上下文工程骨架）⭐⭐⭐⭐⭐
**仓库**: `gsd-build/get-shit-done` | v1.42.3 | 已迁移到 Open GSD

**核心优势**:
- meta-prompting + context engineering + spec-driven 三合一
- 阶段状态机：workspace → discuss → plan → execute → verify → review → ship
- workstreams：并行任务流管理
- milestone summary：里程碑自动汇总
- assumptions mode：假设记录防止AI幻觉
- manager dashboard：任务状态可视化
- /gsd-resume-work：会话恢复，continue-here checkpoint
- /gsd-forensics：事后取证，debug session manager
- 多运行时统一命令（Claude Code / Cursor / Windsurf 等 hyphen form）
- ADR（架构决策记录）ingest to /gsd-plan-phase

**与本地配置的关系**:
- 本地 `.planning/phases/` 对应 GSD 的阶段目录
- 五阶段流程是 GSD 的简化实现
- GSD v1.42.3 的 workstreams 比本地更成熟（并行分支）

**待补强**:
- workstreams 并行任务流 → 本地缺失
- /gsd-forensics 事后调试 → 本地无此工具
- ADR ingest → 本地无架构决策记录机制

---

### 3. Fission-AI/OpenSpec（规格格式骨架）⭐⭐⭐⭐
**仓库**: `Fission-AI/OpenSpec` | v1.4.1 | 支持25+工具

**核心优势**:
- delta specs：只描述变更，不重写全量 spec（brownfield首选）
- 四大制品：proposal.md + specs/ + design.md + tasks.md
- 命令链：/opsx:propose → /opsx:ff → /opsx:apply → /opsx:archive
- /opsx:bulk-archive：自动检测冲突，按时间顺序合并
- 流式渐进：/opsx:continue 单步创建制品，依赖链自动判断
- Custom schemas：可定制工作流，无需修改包代码

**与本地配置的关系**:
- 本地 `openspec/changes/<id>/` 目录完全对齐
- /opsx:propose → /opsx:apply → /opsx:archive 三步流程已实现
- 扩展工作流 `/opsx:new, /opsx:continue, /opsx:ff, /opsx:verify` 已引用但需校验

**待补强**:
- /opsx:onboard：11阶段引导式新人工作流 → 本地无
- Custom schemas 机制 → 本地无自定义 schema 配置

---

### 4. garrytan/gstack（角色 Agents 骨架）⭐⭐⭐⭐⭐
**仓库**: `garrytan/gstack` | 109K Stars | 23个技能

**核心优势**:
- 角色分工虚拟团队：CEO / Eng Manager / Designer / QA Lead / CSO / Release Engineer
- 智能路由：infra bug 跳过 CEO review，UI变更触发 designer，安全变更触发 CSO
- /autoplan：一键串联 CEO→design→eng→DX review 全管线
- /office-hours：六问产品框架，重新定义问题
- 品味记忆学习：跨会话记住设计偏好
- voice-friendly 触发词：自然语言触发对应技能
- /design-shotgun + /design-html：设计探索→生产 HTML 管线
- /qa：真实浏览器测试，发现bug并原子提交修复
- /land-and-deploy：PR合并→CI等待→生产验证→监控

**与本地配置的关系**:
- 本地 agents/ 中 ceo-reviewer / designer / eng-reviewer / security-reviewer 对齐
- gstack 的 codex-reviewer（/codex）在本地已实现
- gstack 的审查路由逻辑（CLAUDE.md审查路由表）已实现
- 本地设计 agents 更完整（design-engineer / design-shotgun 独立存在）

**待补强**:
- 品味记忆：gstack 跨会话记住偏好，本地无此机制
- DX review（开发体验审查）→ 本地缺少
- /land-and-deploy 完整流程 → 本地 land-and-deploy agent 需验证

---

### 5. thedotmack/claude-mem（跨会话记忆骨架）⭐⭐⭐⭐⭐
**仓库**: `thedotmack/claude-mem` | v13.4.0 | 75.8K Stars

**核心优势**:
- 三层工作流：search index → 识别关键IDs → fetch full details（token高效）
- SQLite + ChromaDB 向量搜索（语义检索）
- 4个 MCP 工具：search + get_observations + list_sessions + session_summary
- 平台隔离：Claude/Codex 独立命名空间
- worktree 合并：合并分支时自动整合记忆
- Endless Mode（beta）：生物仿生记忆架构
- File-read 决策门：阻止冗余文件读取，注入 observation timeline
- 24语言 smart-explore（tree-sitter AST）
- 私密标签：`<private>content</private>` 阻止存储敏感信息

**与本地配置的关系**:
- 已作为插件安装（claude-mem 13.4.0）
- 本地 memory-compression / instinct-learning skills 互补
- 本地使用 hooks 管理生命周期

**待补强**:
- 3层检索工作流未在 skills 中明确文档化
- Endless Mode 探索价值

---

## 二、横切关注点分析

### L1 治理层

#### 6. affaan-m/ECC（ECC 防互博 + Hook分级）⭐⭐⭐⭐⭐
**仓库**: `affaan-m/ECC` | v2.0 | 82K Stars

**核心优势**:
- Hook 分级：minimal / standard / strict 三档
- 7种 hook 类型：SessionStart / PreToolUse / PostToolUse / Stop / SessionEnd / PreCompact / UserPromptSubmit
- GateGuard：上下文耗尽/高成本/scope creep/tool loop 警告注入
- AgentShield：102安全规则，912测试（OWASP Top10 + STRIDE）
- Instinct 系统：从会话提取可复用模式，置信度评分（也在本地 instinct-learning skill）
- ECC_HOOK_PROFILE 环境变量控制：minimal/standard/strict
- ECC_DISABLED_HOOKS：按ID禁用特定hook
- PreCompact hook：压缩前保存状态

**关键 hooks（值得复用）**:
- `pre:bash:tmux-reminder`：强制 tmux 运行，保证日志可访问
- `post:edit:typecheck`：编辑后自动类型检查
- `context-monitor`：上下文/成本/loop 监控警告
- `memory-persistence/`：SessionStart/PreCompact/SessionEnd 生命周期内存持久化

**与本地配置的关系**:
- 本地已有 18个 hooks，与 ECC hook 系统并行
- 本地 hooks 已覆盖 SessionStart/PreCompact/Stop 关键生命周期
- 需要对比：本地 hooks vs ECC 是否有功能缺口

**待补强**:
- context-monitor 的 cost warnings 可能优于本地 RTK
- 安全规则集（102条）→ 本地 security-guidance plugin 已部分覆盖

---

### L2 优化层

#### 7. colbymchenry/codegraph（CodeGraph 降本增效）⭐⭐⭐⭐⭐
**仓库**: `colbymchenry/codegraph` | 最新验证 2026-06-02

**核心指标（Opus 4.8 上再验证）**:
- 16% 更便宜 / 47% 减少 tokens / 22% 更快 / 58% 减少工具调用
- 8个 MCP 工具：codegraph_explore / codegraph_search / codegraph_trace / codegraph_impact / codegraph_context / codegraph_affected / codegraph_files / codegraph_status
- 19+语言，13框架感知路由探测
- 本地 SQLite FTS5，无外部 API
- OS文件监视器自动同步
- context synthesis：symbol + dependencies + impact 一次返回

**与本地配置的关系**:
- 已作为 MCP 安装（codegraph MCP dev分组）
- 本地 CLAUDE.md 已有 "codegraph: 47% token减少, 58%调用减少" 引用
- 已在 L3 洞察中定位为代码探索主工具

#### 8. rtk-ai/rtk（Shell 输出压缩）⭐⭐⭐⭐
**仓库**: `rtk-ai/rtk` | Rust 单二进制

**核心优势**:
- 60-90% CLI 输出压缩（git status: ~2000→~200 tokens）
- pre-rewrite hook：自动将 `git status` 重写为 `rtk git status`
- RTK.md 注入模式（Windows fallback）
- 零依赖 Rust 二进制

**与本地配置的关系**:
- 已引用为 "Shell(RTK)" token轨道
- pre-rtk-rewrite hook 已在 hooks/ 中存在

#### 9. JuliusBrussee/caveman（输出Token压缩）⭐⭐⭐⭐
**仓库**: `JuliusBrussee/caveman`

**核心优势**:
- ~65% 输出 token 减少，100% 技术准确度保留
- caveman-compress：~46% CLAUDE.md 等上下文文件压缩
- token 计数器 + 累计节省 + USD 展示
- Conventional Commit + PR one-liner 格式
- 已发表论文验证：简洁约束提升26点准确度

**与本地配置的关系**:
- 已作为 skill 安装（caveman-compress skill）
- 本地 "输出压缩：500字/50%上下文→caveman-compress" 规则已有

---

### L3 洞察层

#### 10. Lum1104/Understand-Anything（项目洞察）⭐⭐⭐⭐⭐
**仓库**: `Lum1104/Understand-Anything` | 52.4K Stars

**核心优势**:
- 多 Agent 管线：file/function/class/dependency 全量提取
- 交互式 Web Dashboard：颜色分层，可搜索可点击
- 命令矩阵：/understand / /understand-chat / /understand-diff / /understand-explain / /understand-onboard / /understand-domain / /understand-knowledge
- post-commit hook 增量更新（仅重分析变更文件）
- knowledge-graph.json：可提交到 git，团队共享
- 中文支持（--language zh）
- 支持 LLM wiki 知识库分析

**与本地配置的关系**:
- 已作为 plugin 安装（understand-anything 2.7.5）
- 本地已有 SessionStart + PostToolUse + 8技能 
- /understand-diff → 结合 codegraph_impact 使用价值更高

---

## 三、辅助工具分析

#### 11. eyaltoledano/claude-task-master（任务管理）⭐⭐⭐⭐
**核心优势**:
- PRD → 结构化任务树（AI自动解析）
- 3模型分工：main(执行) / research(调研) / fallback(降级)
- task-master start <id>：自动启动 Claude Code 带完整上下文
- deferred MCP loading：节省~16% context window (~33K tokens)
- solo/team 两种模式（本地文件 vs 云端 Hamster）

**与本地配置的关系**:
- 已作为可选 MCP（`TASK_MASTER_TOOLS=core`）
- 本地 writing-plans + executing-plans 覆盖核心需求
- task-master 更适合长期多阶段项目管理

#### 12. bytedance/deer-flow（外部编排引擎）⭐⭐⭐
**核心优势**:
- SuperAgent harness：sub-agents + sandboxes + memory
- LangGraph 多智能体编排
- Docker 沙箱隔离，防止主机污染
- 深度调研工作流（多角度交叉验证）
- InfoQuest 智能搜索（BytePlus）

**与本地配置的关系**:
- 已作为可选外部编排（claude-to-deerflow skill）
- /deer-flow 命令支持 flash/standard/pro/ultra 分级
- 主要价值：复杂调研任务 + 长时间自主运行

#### 13. forrestchang/andrej-karpathy-skills（编码原则）⭐⭐⭐⭐
**核心优势**:
- 四原则：不写代码 / 最小代码 / surgical changes / 先思考后编码
- 反模式：premature abstraction / over-engineering
- "Think carefully before writing code"

**与本地配置的关系**:
- 已有 karpathy-guidelines skill（CLAUDE.md 引用）

#### 14. shanraisshan/claude-code-best-practice（最佳实践集）⭐⭐⭐
**核心优势**:
- CLAUDE.md 结构化最佳实践
- 子 Agent 模式
- 上下文管理规则

---

## 四、发现的缺口与冗余

### ✅ 优势（已有且好）
1. 五柱骨架完整：superpowers/GSD/OpenSpec/gstack/claude-mem 全部已安装
2. Token 三轨（RTK+caveman+codegraph）完整
3. 深度调研管线（Firecrawl+Exa）已设计
4. 审查路由（7种reviewer）明确
5. 五阶段流程（①规划→⑤学习）清晰

### ⚠️ 发现缺口
1. **上下文阈值监控缺口**：ECC 的 GateGuard（loop/scope/cost warnings）比本地 context-monitor 更完整
2. **workstreams 并行任务流**：GSD v1.42.3 有，本地没有
3. **ADR（架构决策记录）**：GSD 支持，本地没有 `/adr` 命令
4. **品味记忆**：gstack 学习设计偏好，本地缺失
5. **DX review**：开发体验审查视角缺失
6. **/opsx:onboard**：11阶段引导式 → 本地无等效工具
7. **instinct 系统文档化**：instinct-learning skill 存在但描述不够具体
8. **PreCompact hook 状态保存**：ECC 有专门 memory-persistence lifecycle

### ❌ 冗余/互博风险
1. **understand-anything vs codegraph**：两个都做代码探索，需要明确分工：
   - codegraph：符号级查询（函数/类/调用链），快速低token
   - understand-anything：项目全貌可视化（拓扑图/领域/业务流），面向理解
2. **caveman + RTK + context三轨**：已有明确分工，无互博
3. **deer-flow vs GSD workstreams**：deer-flow 是外部重型编排，GSD 是内部轻量编排，不互博
4. **task-master vs writing-plans**：task-master 面向 PRD驱动的项目级，writing-plans 面向单任务，不互博

---

## 五、各仓库优点提炼汇总

| 仓库 | 核心价值 | 已采纳 | 待补强 |
|------|----------|--------|--------|
| superpowers | SDD+TDD工作流、subagent两阶段审查 | ✅完整 | writing-skills校验 |
| GSD v1.42.3 | 上下文工程、状态机、workstreams | ✅骨架 | workstreams缺失 |
| OpenSpec v1.4.1 | delta spec、四大制品、propose→apply→archive | ✅完整 | onboard引导缺失 |
| gstack v0.19 | 角色团队、智能审查路由、品味记忆 | ✅角色已有 | 品味记忆缺失 |
| claude-mem v13.4.0 | 跨会话记忆、3层检索、平台隔离 | ✅插件已装 | 3层工作流文档化 |
| codegraph | 47%少token、58%少调用、symbol探索 | ✅MCP已装 | 策略更新（先于Grep）|
| ECC hooks | Hook分级、GateGuard、安全规则102条 | 部分 | context-monitor增强 |
| RTK | Shell输出60-90%压缩 | ✅hook已有 | - |
| caveman | 输出65%压缩、memory压缩46% | ✅skill已装 | - |
| Understand-Anything | 交互知识图、domain/diff视角 | ✅插件已装 | diff+codegraph联动 |
| task-master | PRD→任务树、deferred loading | 可选MCP | 按需启用 |
| deer-flow | 外部重型编排、深度调研 | 可选skill | 稳定接口 |
| karpathy | 四原则、最小代码 | ✅skill已有 | - |
| OpenSpec onboard | 11阶段引导 | ❌缺失 | 需添加 |
| GSD workstreams | 并行任务流 | ❌缺失 | 需设计 |
| gstack taste-memory | 品味偏好记忆 | ❌缺失 | 可通过claude-mem实现 |
