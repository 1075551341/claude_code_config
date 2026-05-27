---
name: context-engineering
description: 上下文工程方法，管理上下文窗口质量，防止上下文腐烂。
layer: supplement
source: GSD-redux
---

# Context Engineering

## 核心原则
1. 主上下文保持精简（30-40%），重活在子agent中完成
2. 结构化制品跨会话存活
3. 每个新会话加载制品知道当前位置

## 三级阈值
| 使用率 | 行动 |
|--------|------|
| <40% | 正常工作 |
| 50% | 逻辑断点 /compact |
| 70% | 强制压缩或新子Agent |

## 三态制品管理

| 制品路径 | 用途 | 生命周期 |
|----------|------|----------|
| `openspec/changes/<id>/` | 功能规格变更 | proposal → spec → tasks → archive |
| `.planning/phases/` | 大功能多阶段规划 | discuss → plan → execute → verify → ship |
| `memory/` | 跨会话知识持久化 | claude-mem 渐进式披露，SSOT |

新会话启动：优先加载三态制品 → 其次 rules/CONTEXT.md → 最后对话历史。

## 子Agent编排
- 研究者/计划者/执行者各自 fresh context
- 通过三态制品通信（禁止对话历史传递状态）
- 主窗口只做编排
- DAG依赖图：无依赖并行，有依赖串行

## 压缩策略
- 压缩前快照（pre-compact-state hook，含 openspec/ 状态）
- 保留决策，丢弃细节
- caveman-compress 输出压缩
