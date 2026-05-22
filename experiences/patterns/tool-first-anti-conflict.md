---
category: workflow
confidence: 0.92
date: 2026-05-22
---

# Tool-First 与防互博

## 调用链

MANIFEST → P0 skill → 全局/catalog skill → agent → hook → MCP

## 已验证互斥

| 冲突 | 解决 |
|------|------|
| pre-task-planner vs writing-plans | 禁用 hook，保留 skill + /plan |
| code-review skill vs superpowers 双 skill | 仅保留 requesting/receiving |
| memory MCP vs claude-mem | plugin 跨会话，MCP 临时 |
| RTK vs caveman | shell vs 回复，正交 |

## Token

Shell: RTK | 回复: caveman-compress | 上下文: memory-compression + /compact
