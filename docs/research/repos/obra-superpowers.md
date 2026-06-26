# obra/superpowers v5.1.0 --> v6.0.3

> 层: 五柱(Superpowers) | 置信度: 高 | 刷新: 2026-06-26
> 仓库: github.com/obra/superpowers | 作者: Jesse Vincent (obra/Prime Radiant) | 204K+ stars
> 许可证: MIT | 最新稳定: v5.1.0 (2026-04-30) | 最新: v6.0.3 (2026-06-18)

---

## 核心价值

Superpowers 是一套**可组合的 AI 编码代理技能库与软件开发方法论**，将松散的建议转化为强制性的工程纪律。核心信条:

- **测试驱动开发 — 始终先写测试。**
- **系统性优于临时性 — 流程优于猜测。**
- **复杂性降低 — 简洁为首要目标。**
- **证据优于声明 — 声称完成前先验证。**

### 核心机制

| 机制 | 说明 |
|------|------|
| **HARD-GATE** | 用户批准设计前绝对禁止任何实现代码。无条件、不可绕过。 |
| **SDD+TDD 流水线** | brainstorming -> writing-plans -> subagent-driven-development -> RED-GREEN-REFACTOR |
| **两阶段审查** | Spec Compliance（规格合规）-> Code Quality（代码质量），每任务独立审查 |
| **Fresh Context 隔离** | 每个子Agent fresh context，无上下文污染；Controller 只管编排 |
| **1% 规则** | 即使只有 1% 概率某个 skill 适用，也必须调用。极低阈值，确保不遗漏。 |
| **反合理化表** | 8 种常见内部独白，逐一揭露现实真相。 |
| **指令优先级链** | 用户显式指令 > Superpowers skills > 默认系统提示词 |
| **信任无人规则** | 审查者禁止信任实现者报告，必须通过阅读实际代码验证所有声明。 |

### 跨平台支持 (12 harnesses)

Claude Code | Cursor | Codex App/CLI | Gemini CLI | GitHub Copilot CLI | Kimi Code | Pi | Antigravity | OpenCode | Factory Droid

安装方式: Claude Code 用 /plugin install superpowers@claude-plugins-official; Cursor 用 /add-plugin superpowers。

---

## 技能矩阵 (14 core skills in v5.1.0)

### 开发流水线 (Pipeline Skills, 按执行顺序)

| # | Skill | 触发条件 | 能力 | 门控 |
|---|-------|---------|------|------|
| 1 | **using-superpowers** | 会话开始、任何任务前 | 元技能。1% 规则驱动所有其他 skill 调用。建立指令优先级链。反合理化表。引导恢复。 | 元门控 — 所有其他 skill 的入口 |
| 2 | **brainstorming** | 新功能、变更、问题需要设计探索 | Socratic 设计精炼。9 步强制清单。2-3 方案对比+权衡。逐节审批。设计文档输出。可视化伴侣。 | **HARD-GATE** — 绝对禁止实现代码，直到用户批准设计 |
| 3 | **using-git-worktrees** | 设计批准后、写计划前 | 创建独立分支隔离工作空间。检测是否已在 worktree 内。优先使用 harness 原生工具。需用户同意才创建。来源证明式清理（仅清理 .worktrees/）。 | 环境隔离门 — 确保干净基线 |
| 4 | **writing-plans** | 设计文档批准后 | 将设计分解为 2-5 分钟原子任务。每任务精确文件路径+完整代码+验证命令。无 TBD/TODO（No-Placeholders 规则）。RED-GREEN-REFACTOR 五步强制执行。内联自审（~30s）。 | **Plan Approval Gate** — 用户选择执行模式后才开始实现 |
| 5a | **subagent-driven-development** (推荐) | 实施计划就绪 | 每任务 fresh subagent。v5.1: 两阶段审查（spec->quality）在自然检查点。v6.0: 单一 task-reviewer（一次读diff 双裁决）。模型选择策略（机械->便宜/集成->标准/架构->最强）。实现者状态协议 DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED。Controller 禁止告诉审查者忽略什么。 | 执行门 — 任务级隔离+审查 |
| 5b | **executing-plans** (备选) | 无子Agent能力的 harness | 批量执行+人类检查点。当前会话内执行。停止条件=BLOCKED。 | 执行门 — 批量+人类检查点 |
| 5c | **dispatching-parallel-agents** | 独立无依赖任务可并行 | 并行子Agent工作流。无共享状态。DAG 依赖检测。 | 并行执行门 |
| 6 | **test-driven-development** | 任何实现任务内 | RED-GREEN-REFACTOR: 写失败测试->验证失败->最小代码->验证通过->提交。强制删除先写代码再补测试的代码。测试反模式参考。 | 任务内纪律 |
| 7 | **requesting-code-review** | 完成任务、主要功能、合并前 | 预审查清单。按严重性报告（Critical/Important/Minor）。自包含。行为测试种植真实 bug（SQL注入/明文密码/凭证日志）验证审查者标记。 | 质量门 |
| 8 | **receiving-code-review** | 收到审查反馈、实施建议前 | 需要技术严谨性+验证，非表演性同意。质疑不明确/技术上可疑的反馈。 | 反馈处理门 |
| 9 | **finishing-a-development-branch** | 实现完成、所有测试通过 | 结构化选项: merge/PR/keep/discard。detached HEAD 处理。来源证明式清理。v6.0: forge-neutral。 | **用户选择结果** |

### 调试与验证 (Reactive Skills, 随时触发)

| # | Skill | 触发条件 | 能力 |
|---|-------|---------|------|
| 10 | **systematic-debugging** | 任何 bug、测试失败、意外行为 | 4 阶段根因过程: 调查->模式分析->假设检验->修复验证。刚性 skill — 必须精确遵循。含 root-cause-tracing + defense-in-depth + condition-based-waiting。 |
| 11 | **verification-before-completion** | 即将声称工作完成/修复/通过时 | 证据先行 — 运行验证命令并确认输出后，才可声称成功。防止过早关闭任务。 |

### 元技能

| # | Skill | 触发条件 | 能力 |
|---|-------|---------|------|
| 12 | **writing-skills** | 创建/编辑/验证 skill | 遵循最佳实践创建新 skill。v6.0: 匹配形式到失败模式表格。微测试措辞检查。 |


---

## 工作流链 (Complete SDD+TDD Pipeline)

### 主流水线 (7 阶段, 3 个人类批准门)

Phase 1: Brainstorming (HARD-GATE)
  9步强制清单 -> 探索上下文/视觉伴侣/澄清问题/2-3方案/逐节审批/设计文档/自审/用户审批/过渡
  输出: docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
  门: 用户批准设计 (HARD-GATE, 绝对禁止代码)

Phase 2: Workspace Isolation
  检测环境/请求同意/创建 worktree/验证干净基线
  输出: 隔离的 .worktrees/feature-xxx/ 分支

Phase 3: Writing Plans (Plan Approval Gate)
  文件结构映射/按块组合/计划审查循环/用户选择执行模式
  每任务: RED->GREEN->REFACTOR->Commit
  输出: docs/superpowers/plans/YYYY-MM-DD-<feature>.md

Phase 4: Execution (SDD or Batch)
  SDD: fresh subagent/任务 -> 实施 -> 状态报告 -> 审查(规格/质量) -> 下一任务
  Batch: 批量执行 -> 检查点 -> 人类审查 -> 继续
  门: DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED

Phase 5: TDD (内嵌每任务)
  RED: 写失败测试/验证失败 / GREEN: 最小代码/验证通过 / REFACTOR: 清理/提交

Phase 6: Code Review
  按计划审查 -> 严重性报告 (Critical/Important/Minor)。Critical issues 阻断进度。

Phase 7: Branch Finalization
  验证测试 -> Merge/PR/Keep/Discard -> 清理 worktree
# SDD 实现者状态协议

| 状态 | 含义 | Controller 动作 |
|------|------|-----------------|
| DONE | 工作完成，有信心 | 进入 Stage 1: Spec Compliance Review |
| DONE_WITH_CONCERNS | 完成但有疑虑 | 阅读疑虑，处理正确性/范围后审查 |
| NEEDS_CONTEXT | 信息缺失 | 提供缺失上下文并重新 dispatch |
| BLOCKED | 无法完成任务 | 评估: 提供上下文/升级模型/拆分为更小任务 |

升级黄金法则: 永远不要忽略 BLOCKED 升级，永远不要强制同一模型无变更重试。

### SDD 模型选择策略

| 任务类型 | 模型选择 |
|----------|---------|
| 机械任务 (1-2文件, 完整spec) | 快速便宜模型 |
| 集成任务 (多文件协调, 调试) | 标准模型 |
| 架构/设计/审查任务 | 最强可用模型 |

### v6.0 SDD 关键变更

- 单一 task-reviewer 替代两个独立审查者（一次读diff双裁决）: ~50% token减少 + ~2x速度
- 一次 broad 审查在末尾: 最强模型做全分支审查
- 计划预检: Controller 在第一个任务前检查计划内部冲突
- diff/task text 作为文件传递: task-brief + review-package 脚本
- 每次 dispatch 声明模型: 模板要求模型，较便宜层级指引
- Controller 禁止告诉审查者忽略什么: 禁止压制发现+预评严重性
- 审查者只读+怀疑理由: 不触碰工作树/分支；实现者的意向性选择不覆盖真实发现
- 更强证据+报告: 文件+行号支撑；TDD 时红/绿证据；进度账本允许丢失上下文后恢复

---

## 架构决策

### 1. 双仓库设计 (Dual Repository)

| 仓库 | 内容 | 版本策略 | 更新频率 |
|------|------|---------|---------|
| obra/superpowers (Plugin) | 元数据、hooks、平台 manifest、marketplace 注册 | 语义版本 (5.1.0) | 不频繁 (infra 变更) |
| obra/superpowers-skills (Skills) | 自包含 skill 逻辑、提示词、工作流、脚本 | 滚动/Commit-based | 持续 (每日精炼) |

分离理由: 平台稳定性与快速 skill 改进解耦。Skills 仓库在会话启动时通过 git pull 自动更新。

### 2. 指令优先级层次 (v5.0.0 引入)

1. 用户显式指令 (CLAUDE.md / GEMINI.md / AGENTS.md / 直接请求) -- 最高优先级
2. Superpowers skills -- 中间优先级
3. 默认系统提示词 -- 最低优先级

冲突解决: 如果 CLAUDE.md 说不用 TDD 而 skill 说始终用 TDD，遵循用户指令。用户掌控一切。

### 3. 1% 规则 (Meta-Skill 入口)

即使只有 1% 概率某个 skill 适用，也必须调用。极低阈值确保无相关 skill 被跳过。检查永不可选。

### 4. 反合理化表 (8 种常见借口)

| 合理化想法 | 现实 |
|-----------|------|
| 这只是一个简单问题 | 问题是任务。检查 skills。 |
| 我需要更多上下文 | Skill 检查在澄清问题之前。 |
| 让我先探索代码库 | Skills 告诉你如何探索。先检查。 |
| 这不需要正式 skill | 如果 skill 存在，就使用它。 |
| 我记得这个 skill | Skills 在演进。阅读当前版本。 |
| 这太过度了 | 简单事情变复杂。使用它。 |
| 我先做这一件事 | 做任何事之前先检查。 |
| 这感觉很高效 | 无纪律行动浪费时间。 |

### 5. 上下文隔离原则 (v5.0.2 引入)

所有委派 skills 包含: 子Agent 只接收所需上下文，防止上下文窗口污染。

### 6. 审查循环优化 (v5.0.6 -- 关键转折)

删除子Agent审查循环 -- inline self-review 替代:
- Brainstorming: 子Agent dispatch + 3 迭代上限 -> inline Spec Self-Review (~30s)
- Writing-plans: 子Agent dispatch + 3 迭代上限 -> inline Self-Review (~30s)
- 实证: 5 版本回归测试 x 5 次试验，质量分数相同。审查循环 ~25min 开销无质量提升。
- Self-review 在 ~30s 内捕获 3-5 个真实 bug。

### 7. 视觉伴侣安全模型 (v6.0.0)

每会话密钥、文件服务器沙箱、4h 空闲超时、重启存活。

### 8. SUBAGENT-STOP Gate (v5.0.0)

派发的子Agent 跳过 using-superpowers skill 而非激活 1% 规则。防止递归触发。

### 9. 双 Marketplace 路径 (Claude Code)

官方: /plugin install superpowers@claude-plugins-official
Superpowers 自有: 先 add marketplace obra/superpowers-marketplace，再 install superpowers@superpowers-marketplace

### 10. 贡献者 AI Agent 指南 (v5.1.0)

审计 100 个关闭 PR: 94% AI 生成 PR 被拒。两类强制规则:
- 禁止接受: 第三方依赖、compliance 改写、项目特定配置、批量 PR、推测性修复、领域特定 skills、fork 特定变更、虚构内容、捆绑无关变更。
- 新 harness PR 要求: 会话记录 (acceptance test 必须自动触发 brainstorming)。

---

## 本地映射

### 当前 .claude/ 实现状态

| Superpowers Skill | 本地位置 | 状态 |
|-------------------|---------|------|
| using-superpowers | skills/using-superpowers/SKILL.md (L1) | 已部署 (P0) |
| brainstorming | skills/brainstorming/SKILL.md (L2) | 已部署 (P0) |
| writing-plans | skills/writing-plans/SKILL.md (L2) | 已部署 |
| executing-plans | skills/executing-plans/SKILL.md (L3) | 已部署 |
| subagent-driven-development | skills/subagent-driven-development/SKILL.md (L3) | 已部署 |
| test-driven-development | skills/test-driven-development/SKILL.md (L3) | 已部署 |
| verification-before-completion | skills/verification-before-completion/SKILL.md (L2) | 已部署 (P0) |
| systematic-debugging | skills/systematic-debugging/SKILL.md (L2) | 已部署 (P0) |
| change-impact-analysis | skills/change-impact-analysis/SKILL.md (L1) | 已部署 (P0, 本地扩展) |
| requesting-code-review | skills/requesting-code-review/SKILL.md (L3) | 已部署 |
| receiving-code-review | skills/receiving-code-review/SKILL.md (L3) | 已部署 |
| using-git-worktrees | skills/using-git-worktrees/SKILL.md (L3) | 已部署 |
| finishing-a-development-branch | skills/finishing-a-development-branch/SKILL.md (L3) | 已部署 |
| dispatching-parallel-agents | skills/dispatching-parallel-agents/SKILL.md (L3) | 已部署 |
| writing-skills | skills/writing-skills/SKILL.md (L3) | 已部署 |

### P0 路由集 (5 skills)

L1: using-superpowers + change-impact-analysis
L2 gate: brainstorming + verification-before-completion + systematic-debugging

### 插件加载策略

MANIFEST.yaml -> superpowers.override: local_post_load
-> 插件 5.1.0 自动更新 + 本地 38 skills 后加载覆盖
-> 不删插件 skill，本地覆盖优先

### L0-L4 映射

| 等级 | 机制 | Superpowers 对应 |
|------|------|-----------------|
| L0 | alwaysApply | 本地增强 (无 Superpowers 对应) |
| L1 | 会话常驻 | P0 路由集 + 1% 规则 |
| L2 | 阶段 skill | Pipeline phases + gates |
| L3 | supplement | 其余 skill + review 链 |
| L4 | agents/MCP | SDD subagent dispatch |

---

## 吸收建议

### 已采纳

HARD-GATE | P0 五技能路由 | SDD+TDD 组合 | 两阶段审查 | Fresh context 隔离 | 原子任务 2-5min | 指令优先级链 | 上下文腐烂三级阈值(本地增强) | 反合理化表(部分)

### 适配 (Superpowers -> 本地)

| 项目 | Superpowers | 本地 |
|------|------------|------|
| 工作流阶段 | brainstorm/worktree/plan/SDD/review/finish | 五阶段+ GSD workstreams |
| 门控 | 3 个人类批准门 | HARD-GATE + spec-validation + verification |
| 规格轨道 | 单轨 | 三轨互斥: OpenSpec / GSD / 轻量 spec |
| 审查 | requesting-code-review (通用) | gstack 12 审查者路由 |
| 上下文管理 | Fresh subagent per task | 三级阈值 + GSD 逻辑断点 + 三态制品 |
| 工具路由 | 无 | codegraph(R17) + Firecrawl+Exa + claude-mem(R18) |
| 跨会话记忆 | 无 | claude-mem SSOT + MEMORY.md |
| 变更影响分析 | 无 (依赖 writing-plans) | codegraph_impact + Grep 三阶段 |

### 跳过

视觉伴侣 (Brainstorm Companion) | 双仓库分离 | 多 harness 支持 | marketplace.json 发布 | evals/ 测试子模块 | v6.0 单一 task-reviewer (待观察)

### v6.0 升级决策（v10.2.1 锁定：升级 + 本地 override）

| 特性 | 影响 | 处置 |
|------|------|------|
| 单一 task-reviewer (双裁决) | 50% token减少 + 2x速度 | 采纳，subagent-driven 本地对齐 |
| forge-neutral finishing | 不硬编码 gh pr create | 采纳 |
| 计划预检 (pre-flight read) | Controller首任务前检查冲突 | 采纳 |
| 进度账本 (progress ledger) | 丢失上下文后可恢复 | 采纳 |

### ⚠️ v6.0.0 #1773 回归（本地必须 override）

双源核验（Issue #1773，2026-06-19）：v6.0.0「平台中立」重写 `using-superpowers` 的 Platform Adaptation 段，导致 Claude Code/Cursor 下 **brainstorming 误用原生 `AskUserQuestion`** 结构化选择工具，而非设计意图的「逐条对话式提问」（v5.1.0 行为）。skill 正文几乎未变，回归源于 bootstrap 重写。

**本地 override（D2）**：仅在 `skills/brainstorming/SKILL.md` 加 Cursor/CC 守卫「对话式提问，禁用 AskUserQuestion」。
**边界**：gstack Conductor 故意使用 AskUserQuestion（plain-text 兜底）——证明这是 **per-skill 决策**，故守卫**不全局禁用**，仅约束 brainstorming。

---

## 互博检查

### 与本地工具链冲突

| 工具 A | 工具 B | 冲突 | 严重性 | 解决 |
|--------|--------|------|--------|------|
| Superpowers brainstorming | OpenSpec /opsx:propose | 双设计流程 | 中 | OpenSpec=WHAT, Superpowers=HOW |
| Superpowers writing-plans | OpenSpec tasks.md | writing-plans 不读取 tasks.md | 高 | 手动桥接: brainstorming读取OpenSpec specs |
| Superpowers SDD | agentic-orchestrator | 双编排 | 高 | 禁止同时运行 |
| Superpowers SDD | deer-flow | 双外部编排 | 中高 | deer-flow用于>30min任务；SDD用于流水线内 |
| Superpowers TDD | 本地 SDD+TDD | 规范重叠 | 低 | 互补 |
| Superpowers code-review | gstack 审查路由 | 双审查系统 | 中 | gstack管角色审查, Superpowers管流水线审查 |
| Superpowers worktrees | GSD workstreams | 双worktree管理 | 中 | 统一 .worktrees/ 目录 |
| Superpowers + PlanningWithFiles | -- | 双hook竞争+双追踪 | 高 | 不要合并 |
| Superpowers + GSD | -- | token疯狂消耗 | 高 | 不要同时运行 |
| Superpowers + task-master MCP | -- | 规划职责重叠 | 低 | Superpowers主规划, task-master仅L4 |

### 已知限制

| 限制 | 缓解 |
|------|------|
| 子Agent TDD 跳过 (不自动继承 bootstrap) | 手动触发 using-superpowers |
| 无内置跨会话记忆 | claude-mem + MEMORY.md |
| 无代码知识图谱 | R17 codegraph_explore |
| 无外部搜索集成 | L3 横切 + /deep-research |
| 无上下文腐烂阈值 | 三级阈值 + GSD 逻辑断点 |
| OpenSpec 规格不自动映射 | 手动桥接或 opensuper/specforge |

---

## 最新动态

### v6.0.0 (2026-06-16) -- 重大发布
- SDD 重写: 单一 task-reviewer, ~50% token减少 + ~2x速度
- 新增 Kimi Code + Pi + Antigravity (总计 12 harnesses)
- 视觉伴侣安全模型重写: 每会话密钥、沙箱、4h超时
- Worktree: 全局->项目内 .worktrees/
- Forge-neutral finishing, 计划预检, 进度账本
- Controller禁止告诉审查者忽略什么
- Global Constraints + Per-task Interfaces block (writing-plans)
- evals/ 子模块 (drill-based)
- Skills 工具调用显著更 vendor-neutral

### v6.0.1 (2026-06-16) -- 修补
- Codex 版本显示修复, 更干净同步

### v10.2.1 增量（双源刷新 2026-06-19）
- 本地插件**仍装 5.1.0** → 升级 6.0.0（installed_plugins.json + MANIFEST 对齐）
- **#1773 brainstorming AskUserQuestion 回归** → 本地 brainstorming 守卫（仅此 skill）
- task-reviewer 双裁决正式采纳，subagent-driven-development 本地对齐
- 新增 references/ per-harness 工具映射（Claude Code/Codex/Copilot/Gemini/Pi/Antigravity）→ using-superpowers 指针

### v5.1.0 (2026-04-30) -- 当前本地基准
- 移除遗留 slash commands + named agent
- Worktree Skills 重写 (环境检测/同意/原生工具/来源证明清理)
- SDD: 自然检查点替代每3任务暂停
- Code Review 行为测试 (SQL注入/明文密码/凭证日志)
- 贡献者 AI Agent 指南: 94% AI PR 被拒

### 历史里程碑速览
v5.0.7 (2026-03-31): GitHub Copilot CLI 支持
v5.0.6 (2026-03-24): Inline Self-Review ~25min->~30s (关键转折)
v5.0.5 (2026-03-17): ESM修复, 恢复SDD/inline选择
v5.0.4 (2026-03-16): 单一全计划审查, 审查迭代5->3
v5.0.3 (2026-03-15): Cursor hooks, Bash 5.3+修复
v5.0.2 (2026-03-11): 零依赖Brainstorm Server, 上下文隔离原则
v5.0.1 (2026-03-10): Agentskills合规, Gemini CLI
v5.0.0 (2026-03-09): 目录重构, SDD强制, 视觉伴侣, 指令优先级, SUBAGENT-STOP
v4.3.0 (2026-02-12): HARD-GATE标签引入, EnterPlanMode拦截
v4.0.0 (2026-02-05): 两阶段代码审查, DOT流程图, 测试反模式
v3.2.0: superpowers: 命名空间标准化
v2.0.0: Skills仓库分离

---

### v10.3.1 增量（双源刷新 2026-06-26）

**v6.0.0 → v6.0.3**（GitHub Releases 交叉验证）：
- v6.0.3 (2026-06-18): SDD scratch 文件从 `.git/` 移至 `.superpowers/sdd/`（Claude Code 保护 `.git/` 路径，agent 写入被拒）；progress ledger 改存工作树 git-ignored 目录，`git clean -fdx` 会删除（可从 `git log` 恢复）
- v6.0.2 (2026-06-17): 移除 `evals` 子模块（破坏插件安装），eval harness 独立仓库
- v6.0.0 (2026-06-16): 已记录于 v10.2.1 增量段（task-reviewer 双裁决、forge-neutral、计划预检、进度账本）

**本地影响**：
- SDD scratch 路径变更需 sync 至 `skills/subagent-driven-development/SKILL.md`（如引用 `.git/sdd/`）
- 本地 #1773 brainstorming AskUserQuestion 守卫维持（v6.0.3 未修复该回归）
- 升级决策：v10.2.1 锁定的 6.0.0 升级可推进至 6.0.3（patch 级，无 breaking）

---

## 参考来源

- [GitHub Repository](https://github.com/obra/superpowers)
- [Release Notes](https://github.com/obra/superpowers/blob/main/RELEASE-NOTES.md)
- [v5.1.0 Release](https://github.com/obra/superpowers/releases/tag/v5.1.0)
- [DeepWiki: Key Skills Reference](https://deepwiki.com/obra/superpowers/7-key-skills-reference)
- [DeepWiki: Development Workflows](https://deepwiki.com/obra/superpowers/6-development-workflows)
- [DeepWiki: Brainstorming](https://deepwiki.com/obra/superpowers/7.2-brainstorming)
- [DeepWiki: Writing Plans](https://deepwiki.com/obra/superpowers/7.3-writing-plans)
- [DeepWiki: SDD](https://deepwiki.com/obra/superpowers/7.4-subagent-driven-development)
- [DeepWiki: using-superpowers](https://deepwiki.com/obra/superpowers/7.1-using-superpowers-(meta-skill))
- [DeepWiki: Dual Repository Design](https://deepwiki.com/obra/superpowers/4.1-dual-repository-design)
- [DeepWiki: Release History](https://deepwiki.com/obra/superpowers/10.6-release-history)
- [aidevops: Convolution/Fragility Risk Reassessment](https://github.com/marcusquinn/aidevops/issues/6508)
- [Superpowers + PlanningWithFiles 冲突分析](https://cloud.tencent.com.cn/developer/article/2666142)
- [Superpowers 实战教程](https://cloud.tencent.com.cn/developer/article/2676405)
- [Superpowers vs GSD vs Gstack 对比](https://blog.csdn.net/yangshangwei/article/details/159737473)
- [OpenSpec + Superpowers 协作实战](https://cloud.tencent.com.cn/developer/article/2664183)
- [Superpowers vs Custom Workflows](https://docs.bswen.com/blog/2026-03-26-superpowers-vs-custom-workflows-decision/)
- [SDD: OpenSpec + Superpowers 整合](https://juejin.cn/post/7619871928371183666)
