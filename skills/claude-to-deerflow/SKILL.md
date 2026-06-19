---
name: claude-to-deerflow
description: deer-flow 外部编排引擎桥接。触发词：deer-flow | 外部编排 | LangGraph | 长时任务 | /deer-flow
triggers: [deer-flow, 外部编排, LangGraph, 深度调研, 长时间任务]
layer: supplement
disable-model-invocation: true
loading_tier: L3
source: bytedance/deer-flow
---

# Claude → Deer-Flow 桥接

> **L3 only**：`/deer-flow` 或 >30min 自主任务。常规非简单开发走 subagent-driven；GSD 并行走 workstream-management。**不互替**。

## 何时用

| 场景 | 用 deer-flow | 用本地五阶段 |
|------|-------------|-------------|
| >30min 自主调研 | ✅ | ❌ |
| 多角度交叉验证 + 沙箱 | ✅ | 用 /deep-research |
| ≤3 文件小任务 | ❌ | ✅ |
| 常规功能开发 | ❌ | ✅ executing-plans |

## 接口

```
/deer-flow --mode <flash|standard|pro|ultra> <task描述>
```

| 模式 | 适用 |
|------|------|
| flash | 快速调研，单角度 |
| standard | 默认，2-3 角度 |
| pro | 深度调研 + 沙箱验证 |
| ultra | 长时间多 Agent 编排 |

## 流程

1. 本地 brainstorming 明确调研问题（HARD-GATE）
2. 写入 `.planning/phases/<id>/STATE.md` 记录委托上下文
3. 调用 `/deer-flow --mode standard "<task>"`
4. 结果落盘 `docs/research/<date>-<topic>.md`
5. verification-before-completion 交叉验证结论

## 与 GSD/deer-flow 边界

- **GSD workstreams**：内部并行（git worktree），轻量
- **deer-flow**：外部重型编排（Docker 沙箱、LangGraph）
- 不互博：同一任务只选一种编排

## 失败处理（R16）

deer-flow 不可用 → 报告错误 + 降级 `/deep-research`（Firecrawl+Exa）+ 询问用户是否继续
