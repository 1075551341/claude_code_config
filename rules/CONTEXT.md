---
trigger: model_decision
description: 上下文工程规则 — 详细策略（骨架内容已迁至 CORE.md）
---

# 上下文工程规则

> **骨架内容已迁至 `rules/CORE.md`**：三级阈值、三态制品、DAG依赖图。此处保留详细策略。

## 核心约束

1. **主窗口精简**：主会话仅做编排，重活在子 agent fresh context 中完成
2. **制品存活**：PROJECT.md / REQUIREMENTS.md / ROADMAP.md / STATE.md / CONTEXT.md 跨会话存活
3. **制品优先加载**：新会话首先加载所有结构化制品

## 三级阈值（与 CORE.md 一致）

| 使用率 | Cursor | Claude Code |
|--------|--------|-------------|
| <70% | 正常工作 | 正常工作 |
| 70% | 择机 `/summarize` 或「压缩上下文」 | 择机 `/compact` |
| 90% | 强制 `/summarize` 或新子 Agent | 强制 `/compact` 或新子 Agent |

⛔ 绝不允许达到 100%。Cursor Guard 在 70%/90% 自动注入提醒；实际降低上下文环由 Cursor 原生 `/summarize`（或窗口满时自动 summarize）完成。

**GSD 逻辑断点（70%）**：任务边界 — 完成当前原子任务、切换子 Agent、写入制品；不替代上表压缩阈值。

## 三态制品

子 Agent 间通过三类结构化制品通信，禁止通过对话历史传递状态：

| 制品路径                 | 用途             | 生命周期                                 |
| ------------------------ | ---------------- | ---------------------------------------- |
| `openspec/changes/<id>/` | 功能规格变更     | proposal → spec → tasks → archive        |
| `.planning/phases/`      | 大功能多阶段规划 | discuss → plan → execute → verify → ship |
| `memory/`                | 跨会话知识持久化 | claude-mem 渐进式披露，SSOT              |

新会话启动：优先加载三态制品 → 其次 CONTEXT.md → 最后对话历史。

## Canonical Source Precedence（规范引用链）

> **来源**: GSD-redux | 子 Agent 须逐字引用规范文档，禁止凭记忆转述

| 优先级 | 文档类型                    | 引用方式                 |
| ------ | --------------------------- | ------------------------ |
| 1      | CONTRIBUTING.md / CLAUDE.md | 逐字引用原文             |
| 2      | ADR (docs/adr/\*)           | 逐字引用架构决策         |
| 3      | CONTEXT.md (制品)           | 逐字引用当前事实         |
| 4      | Agent 记忆                  | 仅参考，不可作为决策依据 |

违反此链 = 子 Agent 不可信。规范文档是唯一权威。

## Trust-But-Verify 纪律

> **来源**: GSD-redux | Agent 自述不可信，一律通过 API 直接验证

- 子 Agent 声称"CI 通过"→ 通过 `gh api` 直接查询 check runs 状态
- 子 Agent 声称"测试覆盖完整"→ 检查实际测试文件和覆盖率报告
- 子 Agent 声称"无 lint 错误"→ 运行 lint 命令直接验证
- 违反验证纪律 = DONE_WITH_CONCERNS，需补充验证证据

## 子 Agent 调度原则

- 研究者/计划者/执行者各自 fresh context（窗口随 `model` / `config/model-context-windows.json` 解析，勿写死）
- 通过三态制品通信（不通过对话历史）
- 每个子任务独立原子提交
- 主窗口保持在 30-40% 上下文使用率

> **DAG 编排**详见 `rules/WORKFLOW.md`

## 压缩策略

| 编辑器 | 显式压缩 | 压缩前快照 | 结构化摘要（不压缩） |
|--------|----------|------------|----------------------|
| **Cursor** | `/summarize` 或「压缩上下文」 | `preCompact` → `~/.cursor/.state/pre-compact-state.json` | 「提取上下文」→ `session-digest.md` |
| **Claude Code** | `/compact`（**70% 原生自动**；hook 70% 建议 / 90% 强制） | `pre-compact-state` hook | Guard 摘要制品 + claude-mem |

1. 保留：决策、状态、制品
2. 丢弃：中间推理、已验证的细节
3. 输出精简 → `caveman-compress` skill（回复侧）

## 长任务治理

- 超过 30 分钟 → 拆分为独立子 Agent
- 每完成一个子目标 → 输出状态摘要 + 释放上下文
- 工作流切换 → 保存/恢复规划上下文

## deer-flow 外部编排引擎（optional）

> **来源**: bytedance/deer-flow 2.0 | LangGraph-based SuperAgent harness | 70K+ stars

**何时考虑启用**:
- 长时任务（>30分钟）需要外部编排
- 需要 Sandbox 隔离执行（Docker）
- 需要子 Agent 并发（max 3, 15min timeout）

**四执行模式**: flash(快速) / standard(标准) / pro(规划) / ultra(子Agent并行fan-out)
**集成方式**: `claude-to-deerflow` skill → `npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow`

**不启用时**: 使用本地 subagent-driven-development + agentic-orchestrator 实现类似效果。

## claude-context MCP（optional）

来源：zilliztech/claude-context | 配置：`mcp-configs/dev.json` → `optional.claude-context`

**启用条件**（满足 ≥2）：

1. **Monorepo** — 多包/多模块，grep 不足以定位
2. **已有向量索引** — 可部署 claude-context 服务
3. **与 GSD 互补** — 不替代 <70/90% 阈值与 claude-mem SSOT

**不启用时**：用 code-explorer agent + ctx7 MCP + 项目 `CONTEXT.md`。

## 外部搜索策略（Firecrawl / Exa）

> **来源**: L3 洞察横切 | 深度调研默认走 `/deep-research` 管线

| 意图 | 工具 |
|------|------|
| 网页抓取 / 文档站 / 竞品页 | Firecrawl（`crawl` MCP 或 firecrawl CLI） |
| 语义搜索 / 学术与新闻 | Exa（Cursor 插件 MCP） |
| 库/API 官方文档 | Context7 MCP |
| 多角度交叉验证 | `skills/deep-research` 四阶段流程（L3） |

禁止仅凭训练数据做时效性断言；矛盾来源须显式列出。

## codegraph MCP 使用策略

> **来源**: colbymchenry/codegraph | 预索引知识图谱，~35% token 节省，~70% 工具调用减少

**何时用 codegraph（而非 explore agent）**：

- 项目已有 `.codegraph/` 索引（`codegraph init -i`）
- 问"X 如何调用 Y"、"这个函数的调用链"等结构性问题
- 需要在改代码前评估影响范围
- 大项目（>500 文件）中探索性搜索

**工具选择指南**：
| 意图 | 工具 |
|------|------|
| 了解某个区域 | `codegraph_context` |
| "X 如何到达 Y" | `codegraph_trace` |
| 找调用者/被调用者 | `codegraph_callers` / `codegraph_callees` |
| 改代码前评估影响 | `codegraph_impact` |
| 查找符号 | `codegraph_search` |
| 批量读取符号源码 | `codegraph_explore` |
| 检查索引新鲜度 | `codegraph_status` |

**规则**：

- codegraph 返回的源码视为已读取，不重复 grep/Read
- 无 `.codegraph/` 时回退到 explore agent
- 编辑后检查 staleness banner：有 ⚠️ 时 Read 文件直接获取最新内容

## Understand-Anything 使用策略

> **来源**: Lum1104/Understand-Anything v2.7.5 | 交互知识图 + 引导导览

**何时用 UA（而非 codegraph）**：

- 新项目接手需理解架构概念 → `/understand --review`
- 领域驱动分析/业务聚类 → `/understand-domain`
- 新人 onboarding 导览 → `/understand-onboard`
- 交互式问答（基于图谱） → `/understand-chat`
- 修改前影响评估 → `/understand-diff`

**双引擎协同**：
| 场景 | 首选 | 补充 |
|------|------|------|
| 代码结构/调用链查询 | codegraph | — |
| 概念理解/架构导览 | UA | — |
| 探索未知代码 | codegraph 查结构 | UA 查概念 |
| 新人 onboarding | UA 导览 | codegraph 补充细节 |

## claude-mem 三层搜索工作流

> **来源**: thedotmack/claude-mem v13 | token 高效渐进式检索

```
search（compact index, ~50-100 tokens/条）
  ↓ 筛选相关 ID
timeline（时间线上下文）
  ↓ 确认相关性
get_observations（完整详情, ~500-1000 tokens/条）
```

~10x token 节省：先过滤再取详情，而非一次拉全量。

## 自改进要点

> **source**: [kumaran-is/claude-code-guide](https://github.com/kumaran-is/claude-code-guide)

- 错误恢复：失败模式写入 `experiences/rejected/`，成功模式写入 `experiences/patterns/`
- 会话切换：优先加载制品（Cursor：`@session-digest.md` + handoff）；先「提取上下文」再压缩，避免丢失决策
- 长任务：每子目标完成后输出状态摘要，便于 stop-pattern-extraction 提取
