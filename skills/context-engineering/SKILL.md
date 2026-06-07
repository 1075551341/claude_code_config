---
name: context-engineering
description: 上下文工程方法，管理上下文窗口质量，防止上下文腐烂。
layer: supplement
source: GSD-redux
---

# Context Engineering

## 核心原则

1. 主上下文保持精简（30-40%），重活在子 agent 中完成
2. 结构化制品跨会话存活
3. 每个新会话加载制品知道当前位置

## 三级阈值

| 使用率 | 行动                 |
| ------ | -------------------- |
| <70%   | 正常工作             |
| 70%    | 择机 /compact        |
| 90%    | 强制压缩或新子 Agent |

## 三态制品管理

| 制品路径                 | 用途             | 生命周期                                 |
| ------------------------ | ---------------- | ---------------------------------------- |
| `openspec/changes/<id>/` | 功能规格变更     | proposal → spec → tasks → archive        |
| `.planning/phases/`      | 大功能多阶段规划 | discuss → plan → execute → verify → ship |
| `memory/`                | 跨会话知识持久化 | claude-mem 渐进式披露，SSOT              |

新会话启动：优先加载三态制品 → 其次 rules/CONTEXT.md → 最后对话历史。

## 子 Agent 编排

- 研究者/计划者/执行者各自 fresh context
- 通过三态制品通信（禁止对话历史传递状态）
- 主窗口只做编排
- DAG 依赖图：无依赖并行，有依赖串行

## 压缩策略

- 压缩前快照（pre-compact-state hook，含 openspec/ 状态）
- 保留决策，丢弃细节
- caveman-compress 输出压缩

## 项目洞察集成

- **codegraph MCP**：代码结构查询优先用 codegraph，替代 Grep 大量搜索（~35% token 节省）
- **Understand-Anything**：概念理解/架构导览用 UA，新人 onboarding/领域分析
- **协同**：探索代码 → codegraph 查结构 → UA 查概念 → 合并结果
