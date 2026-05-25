---
name: context-engineering
description: 上下文工程规则，管理上下文窗口质量与子agent调度
alwaysApply: false
layer: supplement
source: gsd-build/get-shit-done + zilliztech/claude-context
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

## 子Agent调度原则

- 研究者/计划者/执行者各自 fresh context（200K token）
- 通过结构化制品通信（不通过对话历史）
- 每个子任务独立原子提交
- 主窗口保持在 30-40% 上下文使用率

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
