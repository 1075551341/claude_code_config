---
name: memory-compression
description: 上下文压缩与跨会话记忆协调。触发：记忆压缩、上下文腐败、/compact。
layer: supplement
source: thedotmack/claude-mem + GSD-redux
disable-model-invocation: true
loading_tier: L3
---

# 记忆压缩

## 职责边界（防互博）

| 层 | 负责 | 不做 |
|----|------|------|
| **claude-mem plugin** | 跨会话持久化、mem-search | 不重复写 skill 正文 |
| **本 skill** | 压缩策略、阈值、摘要格式 | 不替代 plugin 存储 |
| **memory MCP** | 会话内临时节点 | 非长期 SSOT |
| **hook/pre-compact-state** | 压缩前状态快照 | — |

## 触发

- 上下文 >70% → `/compact` 或委派 agent/context-manager
- 逻辑断点（子目标完成）→ 摘要后释放
- 会话结束 → claude-mem plugin 持久化

## 压缩策略（v11 自 /compact 并入）

1. 保留：关键决策、当前任务状态、用户偏好、未解决问题
2. 丢弃：已完成子任务细节、中间错误重试日志、冗余文件内容
3. 摘要：当前进度、下一步计划、已知风险

## 摘要输出格式（v11 自 /compact 并入）

```
## 当前状态
- 已完成: [子目标列表]
- 进行中: [当前任务 + 进度]
- 待处理: [剩余任务列表]

## 关键决策
- [决策 1] — [原因]

## 下一步
1. [立即执行的任务]
```

## 压缩格式

```json
{ "category": "决策|偏好|架构|错误", "key": "...", "value": "...", "confidence": 0.9 }
```

高置信度模式/拒绝模式 → claude-mem observation（R18；原 `experiences/` 文件体系已归档至 `docs/archive/experiences/`）

## 来源

claude-mem + GSD-redux
