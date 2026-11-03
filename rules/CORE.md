---
trigger: always_on
alwaysApply: true
layer: skeleton
description: 始终启用 — 铁律唯一正文 + 工具优先级 + 上下文阈值 + 编码约束
---

# CORE — 铁律与开发习惯

> 只保留**方向性禁令**、**开发习惯**、**编码约束**、**流程补充**。阶段/门控/完成定义 → `config/workflow.yaml`（派生到 `CLAUDE.md`）。模型与推理强度不由本包决定。

## 铁律（唯一正文；编号稳定，R2/R6/R7/R10 已于 v13 退役）

| # | 约束 | 内容 |
| --- | --- | --- |
| R1 | 完成 | 完成 = 观察到的验证证据 + **本轮全新独立审查 PASS**（两道门：符合预期要求 + 原功能保持）。缺任一 = 未完成；轮次用尽 = BLOCKED。站立目标 `/goal` = 同一两道门（`completion.standing_goal`），不是第三道 |
| R3 | Bug 修复 | Grep 同类模式全修，再 Grep 确认 0 |
| R4 | 配置变更 | Grep 全部引用方 → 构建 / validate 通过 |
| R5 | 重试上限 | 同方案 ≤2 次，第 3 次换方案或上报 |
| R8 | 高危确认 | 删数据、覆盖、强推、数据迁移前须用户确认 |
| R9 | 命令安全 | Windows 一律 `pwsh` 7.5+（缺则 BLOCKED）；禁 `powershell -Command`、禁 cd+重定向；MCP spawn → `rules/MCP.md` |
| R11 | 安全默认 | 不信任外部输入；无硬编码密钥；环境配置走 `.env` |
| R12 | 子 Agent 隔离 | fresh context + 制品通信，禁止共享可变状态 |
| R13 | 制品存活 | PROJECT/REQUIREMENTS/ROADMAP/STATE/CONTEXT 跨会话持久化 |
| R14 | 版本克制 | 非必要不升 major；major 需明确收益或用户确认 |
| R15 | 包管理器 | Node 用 pnpm 11，尊重 lockfile；缺声明的管理器 → BLOCKED，禁止改用 npm（安装 → `config/toolchain.yaml`） |
| R16 | 错误暴露 | 禁止裸 `except: pass` / 静默吞错；异常传播或显式处理并报告 |
| R17 | 代码探索 | codegraph 首选，禁止跳级（见下）；codebase-memory 已禁用 |
| R18 | 记忆优先 | 「为什么 / 约定 / 偏好」查 claude-mem，不塞进 codegraph |
| R19 | Git 禁令 | 禁止自动 `git stash` / `git commit`（仅用户显式指令）；禁止 force push main/master |
| R20 | 会话终验 | 七维回放（满足/遗漏/错改/漏改/原功能/影响范围/**问题是否解决**）+ 配置/修改与文档/注释同步 + 审查前刷图 + 每轮全新开审；修改只走 `change-implementer`；证据须观察输出。政策 → verification skill |

<!-- engineering-rules:start -->
### 工程原则（R21-R25，按类型合并）

> 铁律的工程决策组；只答方案选择，不改 R1-R20 流程门；安全/合规/不可逆为硬底线。

#### R21 核心思想
- **R21.1 第一性原理**：先理解真实目标与约束，再选方案。
- **R21.2 本质优先/YAGNI**：先解本质；不为假设未来过度设计。
- **R21.3 可维护的最简**：守可维护/可测试/可回滚下限，再取最简。

#### R22 简洁与设计
- **R22.1 KISS**：简单直接，避免多余复杂度。
- **R22.2 DRY**：重复逻辑第三次或成本有证据才抽象。
- **R22.3 SOLID**：职责清晰、低耦合；接口/扩展点第二变化点后再抽象。

#### R23 架构
- **R23.1 删除优先于兼容**：内部代码直接删；公共契约先弃用 + 迁移说明；删除限于本次变更影响面。
- **R23.2 不做过早/未验证架构**：不引入未验证抽象/配置/间接层。
- **R23.3 最小可用、逐步演进**：MVP 只缩范围；每次修改建立在可运行系统上；不降 R1/R20；缩范围需用户批准，或已写入经用户批准的验收标准；不得静默缩 scope。
- **R23.4 当前可用性优先**：不为未来复杂度牺牲当前可用性。

#### R24 代码质量
- **R24.1 职责单一**：按变更原因拆分模块。
- **R24.2 成熟方案优先**：优先成熟库；复杂/安全敏感不手搓。
- **R24.3 依赖克制**：已有代码/依赖/文档优先；新增需理由。
- **R24.4 先检查再引入**：先查已有代码/依赖/文档/能力。
- **R24.5 反对优雅复杂度**：优雅 = 更少概念、更低变更成本。

#### R25 工程决策
- **R25.1 长期可维护优先**：长期优先，以 R21.3 为约束。
- **R25.2 业务目标优先**：服务业务，不展示技术复杂度。
- **R25.3 简单满足即不升级**：够用即止。

#### 冲突裁决（R 组）

| 冲突 | 裁决 |
|---|---|
| R21.1 / R24.2 | 原理决定是否自建；商品化默认 R24.2。 |
| R21.1 / R25.2 | 业务定“为什么”，本质定“做什么”；不以紧迫跳过正确性/安全。 |
| R21.3 / R25.1 | 长期优先以 R21.3 的可维护/可测试/可回滚下限为约束。 |
| R22.1 / R22.3 | 设计 R22.1；R22.3 第二个变化点后启用。 |
| R22.2 / R24.5 | R22.2 第三次或成本有证据才抽象；R24.5 反对为优雅加层。 |
| R23.1 / R14 | R23.1 管内部代码删除；公共契约按 R23.1 弃用 + 迁移；R14 约束 major 版本升级。 |
| R23.3 / R1、R20 | R23.3 只缩范围，不降验证/审查。 |
| R23.4、R25.2 / R25.1 | 可见行为 R23.4/R25.2；内部结构 R25.1（需证据）。 |
| R24.2 / R24.3 | R24.3 先查已有依赖；R24.2 仅在成熟库 TCO 更低时新增。 |

> 完整案例/溯源 → `~/.claude/docs/ENGINEERING_PRINCIPLES.md`；编码约束 → 本 harness 的 CORE 规则；C8 仅详参 docs（R23.2 不禁止设计/spike）。
<!-- engineering-rules:end -->

## 开发习惯

- 先想后写：说出假设与歧义，不确定就问；先把任务改写成可验证的成功标准，再动手。
- 改前先查影响面：有 `.code-review-graph/` 时 CRG `get_minimal_context` + `get_impact_radius`（有 diff 再 `detect_changes`），叠加 `codegraph_explore` blast-radius；改名/删除/移动后 Grep 残留 = 0；改 agent/skill/rule/hook/MCP 同步 INDEX + MANIFEST。
- 一次改齐：清单内文件按拓扑序一轮改完，不「先改一点再看」。
- 最小改动集：只改与需求直接相关的文件/行；不顺手重构、不扩大范围。
- 工程原则（R21-R25）已并入本文件 `## 铁律`；除铁律正文外，本文件只保留流程/编码习惯。
- 改了行为就同步文档、注释、README、CHANGELOG、版本戳。
- 测试：新功能有覆盖；Bug 修复先写复现；不跳过/禁用测试。Playwright / chrome-devtools 浏览器 UI 测试仅用户显式要求才跑；未要求但任务强烈像需要 → interrupt，禁止静默开跑或软自动兜底（SSOT → `rules/MCP.md` §2c / `mcp/servers.json` `browser_ui_tests`）。不另建 Stop hook，也不构成第三道 `/goal` 门。
- 业务逻辑禁用裸 `new Date()` / `Date.now()` / `datetime.now()`：用时区库 + Clock 注入（CLI 一次性脚本、纯展示除外）；TS 用 dayjs。
- 文件编码：UTF-8 无 BOM，保留目标文件编码/BOM/EOL；文件内容一律用 Edit/Write 工具写，禁止 shell 重定向写内容；发现乱码立即回滚原片段，禁止在损坏内容上叠加修改。
- 沟通语言：中文；代码块仅在需要时输出。Git 规范 → `rules/GIT.md`；交付 → `skills/ship`。

## 编码约束

- 不可变优先（新对象/展开/map/filter，不原地改）；每层显式处理错误，禁止静默吞错，异步必 try/catch。
- 系统边界验证所有外部输入；安全默认（R11）。
- UI/API/表/migration：改 schema 必须带 migration；API 变更同步版本/文档；破坏性变更写迁移说明。
- 热路径先测量再优化；I/O 批量，避免 N+1；多小文件优于少大文件（典型 200–400 行）。
- 引用代码带 `file:line`；不添加注释除非要求。

## 执行并发

<!-- spine:concurrency -->
**执行并发**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：无依赖且可后台的命令/操作不得阻塞会话，优先并行。有依赖或下一步需要其输出的仍按序、禁止后台。长驻服务器 / watcher 保持后台。不是第三道 PASS 门，不另建 Stop hook，不改 `browser_ui_tests`。

- 无依赖且可后台的命令/操作不得阻塞会话，优先并行
- 有依赖或下一步需要其输出的步骤仍按序执行，禁止后台
- 长驻服务器 / watcher 保持后台
<!-- /spine:concurrency -->

## R17-R18 工具优先级（严格递进，禁止跳级）

| 需求 | 首选 | 禁止 |
| --- | --- | --- |
| 函数/类/调用链/「怎么运作」 | `codegraph_explore` | 跳过 codegraph 直接 Grep/Read/Glob/everything |
| 精准上下文 / 变更影响 | CRG `get_minimal_context` + `get_impact_radius` | 凭直觉估范围 |
| 风险门禁 / 审查 / 开 PR | CRG `detect_changes` + `get_review_context` | 用 codegraph 做 test-gap |
| 为什么 / 约定 / 偏好 | claude-mem search → get_observations | 往 codegraph 塞偏好 |
| 本机按文件名（跨仓/全盘） | `everything_search`（Windows） | 用 everything 替代 Glob 或 codegraph |

`codegraph_explore` 返回的源码视为已读，禁止重复 Read/Grep。Grep 仅在双图就绪后作残留核对。

**图谱三时点**（`hooks/_lib/graph_freshness.py`）：任务开始 SessionStart `ensure`（无图 → PreToolUse deny 探索/编辑）→ 每轮独立审查前在 `last_edit` 之后增量 refresh（`last_pre_review_graph_ts > last_edit_ts` 才可派审，失败禁止开审）→ 完成后 Stop refresh（不计为审查前刷新）。

## 上下文阈值

⛔ 绝不允许达到 100%。

| 使用率 | Cursor | Claude Code |
| --- | --- | --- |
| 70% | 择机 `/summarize`（或「压缩上下文」） | 择机 `/compact` |
| 90% | 强制 `/summarize` 或新子 Agent | 强制 `/compact` 或新子 Agent |

GSD 70% 是逻辑断点：完成当前原子任务、切子 Agent 或写制品，不等于强制压缩。窗口大小由调用方的模型与设置决定（`hooks/_lib/context_thresholds.py`）。

## 错误升级

重试（瞬态，≤R5）→ 降级（非核心能力不可用时继续并在报告中注明；完成仍须独立审查 PASS）→ 需确认（权限/冲突/数据风险）→ 硬阻断（安全/不可逆，立即停止并报告）。不确定时升级，不猜。
