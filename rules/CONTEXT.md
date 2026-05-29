---
name: context-engineering
description: 上下文工程规则，管理上下文窗口质量与子agent调度
alwaysApply: false
layer: supplement
source: open-gsd/get-shit-done-redux + zilliztech/claude-context + colbymchenry/codegraph + thedotmack/claude-mem
triggers:
  - 上下文管理
  - 子agent调度
  - 上下文腐烂
---

# 上下文工程规则

## 核心约束

1. **主窗口精简**：主会话仅做编排，重活在子agent fresh context中完成
2. **制品存活**：PROJECT.md / REQUIREMENTS.md / ROADMAP.md / STATE.md / CONTEXT.md 跨会话存活
3. **制品优先加载**：新会话首先加载所有结构化制品

## 上下文腐烂三级阈值

| 使用率 | 行动 |
|--------|------|
| <40% | 正常工作（主会话编排 + 子agent实现） |
| 50% | 逻辑断点 `/compact`，释放已完成上下文 |
| 70% | 强制压缩或启动新子Agent，保留决策丢弃细节 |

## 三态制品

子Agent间通过三类结构化制品通信，禁止通过对话历史传递状态：

| 制品路径 | 用途 | 生命周期 |
|----------|------|----------|
| `openspec/changes/<id>/` | 功能规格变更 | proposal → spec → tasks → archive |
| `.planning/phases/` | 大功能多阶段规划 | discuss → plan → execute → verify → ship |
| `memory/` | 跨会话知识持久化 | claude-mem 渐进式披露，SSOT |

新会话启动：优先加载三态制品 → 其次 rules/CONTEXT.md → 最后对话历史。

## Canonical Source Precedence（规范引用链）

> **来源**: GSD-redux | 子Agent 须逐字引用规范文档，禁止凭记忆转述

| 优先级 | 文档类型 | 引用方式 |
|--------|---------|---------|
| 1 | CONTRIBUTING.md / CLAUDE.md | 逐字引用原文 |
| 2 | ADR (docs/adr/*) | 逐字引用架构决策 |
| 3 | CONTEXT.md (制品) | 逐字引用当前事实 |
| 4 | Agent 记忆 | 仅参考，不可作为决策依据 |

违反此链 = 子Agent 不可信。规范文档是唯一权威。

## Trust-But-Verify 纪律

> **来源**: GSD-redux | Agent 自述不可信，一律通过 API 直接验证

- 子Agent 声称"CI 通过"→ 通过 `gh api` 直接查询 check runs 状态
- 子Agent 声称"测试覆盖完整"→ 检查实际测试文件和覆盖率报告
- 子Agent 声称"无 lint 错误"→ 运行 lint 命令直接验证
- 违反验证纪律 = DONE_WITH_CONCERNS，需补充验证证据

## 子Agent调度原则

- 研究者/计划者/执行者各自 fresh context（200K token）
- 通过三态制品通信（不通过对话历史）
- 每个子任务独立原子提交
- 主窗口保持在 30-40% 上下文使用率

### DAG 依赖图规则

```
无依赖子目标 → 并行派发（同一批次内共享三态制品快照）
有依赖子目标 → 等待前置完成 + 制品写入后派发
冲突检测：同一制品路径禁止并行写入
```

## 压缩策略

1. 压缩前快照 → `pre-compact-state` hook
2. 保留：决策、状态、制品
3. 丢弃：中间推理、已验证的细节
4. 输出压缩 → `caveman-compress` skill

## 长任务治理

- 超过30分钟 → 拆分为独立子Agent
- 每完成一个子目标 → 输出状态摘要 + 释放上下文
- 工作流切换 → 保存/恢复规划上下文

## claude-context MCP（optional）

来源：zilliztech/claude-context | 配置：`mcp-configs/dev.json` → `optional.claude-context`

**启用条件**（满足 ≥2）：

1. **Monorepo** — 多包/多模块，grep 不足以定位
2. **已有向量索引** — 可部署 claude-context 服务
3. **与 GSD 互补** — 不替代 <40/50/70% 阈值与 claude-mem SSOT

**不启用时**：用 code-explorer agent + ctx7 MCP + 项目 `CONTEXT.md`。

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
- 会话切换：优先 `/clear` 加载制品，避免 `/compact` 丢失决策上下文
- 长任务：每子目标完成后输出状态摘要，便于 stop-pattern-extraction 提取
