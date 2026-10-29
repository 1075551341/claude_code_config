---
trigger: always_on
alwaysApply: true
layer: skeleton
description: 始终启用 — 铁律唯一正文 + 工具优先级 + 上下文阈值 + 编码约束
---

# CORE — 铁律与开发习惯

> 只保留**方向性禁令**、**开发习惯**、**流程补充**。阶段/门控/完成定义 → `config/workflow.yaml`（派生到 `CLAUDE.md`）。模型与推理强度不由本包决定。

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

## 开发习惯

- 先想后写：说出假设与歧义，不确定就问；先把任务改写成可验证的成功标准，再动手。
- 改前先查影响面：有 `.code-review-graph/` 时 CRG `get_minimal_context` + `get_impact_radius`（有 diff 再 `detect_changes`），叠加 `codegraph_explore` blast-radius；改名/删除/移动后 Grep 残留 = 0；改 agent/skill/rule/hook/MCP 同步 INDEX + MANIFEST。
- 一次改齐：清单内文件按拓扑序一轮改完，不「先改一点再看」。
- 最小改动集；删除过时代码优先于加兼容层/fallback；不为假设需求设计（YAGNI）；不为消除少量重复做抽象。
- 依赖克制：先用已有依赖与能力；新增依赖需理由。
- 改了行为就同步文档、注释、README、CHANGELOG、版本戳。
- 测试：新功能有覆盖；Bug 修复先写复现；不跳过/禁用测试。Playwright / chrome-devtools 浏览器 UI 测试仅用户显式要求才跑；未要求但任务强烈像需要 → interrupt，禁止静默开跑或软自动兜底（SSOT → `rules/MCP.md` §2c / `mcp/servers.json` `browser_ui_tests`）。不另建 Stop hook，也不构成第三道 `/goal` 门。
- 业务逻辑禁用裸 `new Date()` / `Date.now()` / `datetime.now()`：用时区库 + Clock 注入（CLI 一次性脚本、纯展示除外）。
- 文件编码：UTF-8 无 BOM，保留目标文件编码/BOM/EOL；文件内容一律用 Edit/Write 工具写，禁止 shell 重定向写内容；发现乱码立即回滚原片段，禁止在损坏内容上叠加修改。
- 沟通语言：中文；代码块仅在需要时输出。Git 规范 → `rules/GIT.md`；交付 → `skills/ship`。

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
