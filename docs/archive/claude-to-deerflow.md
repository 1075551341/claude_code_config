# 历史资料：claude-to-deerflow

> 2026-11-15 移出技能发现路径。仅用于了解旧设计，文中命令与组件不构成当前可执行配置。
> 旧版源归属保留；当前策略及来源核查见本轮研究记录。


# Claude → Deer-Flow 桥接

> **L3 only**：deer-flow（外部 CLI）或 >30min 自主任务。常规非简单开发走 executing-plans（主会话内联）；并行任务按项目需要选择工具。**不互替**。

## 何时用

| 场景                                   | 用 deer-flow | 用本地工作流       |
| -------------------------------------- | ------------ | ------------------ |
| >30min 自主调研                        | ✅           | ❌                 |
| 多角度交叉验证 + 沙箱                  | ✅           | 用 /deep-research  |
| 简单(task-triage判定=关联需改≤2)小任务 | ❌           | ✅                 |
| 常规功能开发                           | ❌           | ✅ executing-plans |

## 接口

```
deer-flow --mode <flash|standard|pro|ultra> <task描述>
```

| 模式     | 适用                |
| -------- | ------------------- |
| flash    | 快速调研，单角度    |
| standard | 默认，2-3 角度      |
| pro      | 深度调研 + 沙箱验证 |
| ultra    | 长时间多 Agent 编排 |

## 流程

1. 本地 brainstorming 明确调研问题（HARD-GATE）
2. 写入 `spec/<project>/STATE.md` 记录委托上下文
3. 调用 deer-flow CLI（`--mode standard "<task>"`）
4. 结果落盘 `docs/research/<date>-<topic>.md`
5. verification-before-completion 交叉验证结论

## 与 deer-flow 边界

- **deer-flow**：外部重型编排（Docker 沙箱、LangGraph）
- 不互博：同一任务只选一种编排

## 失败处理（R12）

deer-flow 不可用 → 报告错误 + 降级 `/deep-research`（Firecrawl+Exa）+ 询问用户是否继续
