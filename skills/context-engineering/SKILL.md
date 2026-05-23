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

## 子Agent编排
- 研究者/计划者/执行者各自 fresh context
- 通过结构化制品通信
- 主窗口只做编排

## 压缩策略
- 压缩前快照（pre-compact-state hook）
- 保留决策，丢弃细节
- caveman-compress 输出压缩
