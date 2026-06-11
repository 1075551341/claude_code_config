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

## 压缩格式

```json
{ "category": "决策|偏好|架构|错误", "key": "...", "value": "...", "confidence": 0.9 }
```

高置信度模式 → `experiences/patterns/`；拒绝模式 → `experiences/rejected/`

## 来源

claude-mem + GSD-redux
