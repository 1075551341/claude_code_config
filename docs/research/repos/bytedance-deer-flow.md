# bytedance/deer-flow v2.0

> 层: L1 治理 | 置信度: 中 | 刷新: 2026-06-16

## 核心价值

- flash/standard/pro/ultra 四模式自主编排
- LangGraph + 9 middleware
- Docker sandbox 隔离执行
- 适用于 >30min 长时自主任务
- 外部编排，不替代 Superpowers 内部子 Agent

## 证据

- [GitHub bytedance/deer-flow](https://github.com/bytedance/deer-flow)
- v2.0 LangGraph 架构

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| deer-flow bridge | `skills/claude-to-deerflow/SKILL.md` (L3) |
| 互斥 | MANIFEST excludes `[deer_flow, workstream_management]` |
| 触发 | `CLAUDE.md` → `/deer-flow` L3 |

## 吸收决策

**catalog/L3 可选** — 与 workstream-management 互斥；Superpowers 内部编排为主。

## 互博检查

- vs workstream：MANIFEST conflict 声明
- vs ruflo：不并行部署外部编排

## v10.1 增量

- 维持 L3 可选；无默认启用变更
- 访谈确认编排策略不变
