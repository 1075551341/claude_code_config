# bytedance/deer-flow v3.1

> 层: L1 治理 | 置信度: 中 | 刷新: 2026-06-24 | 来源: GitHub + CSDN + awesomeagents.ai 三源交叉

## 核心价值

- v3.1(2026-05-02)：LangGraph 1.0 从零重写，50K+ Stars
- 11 层中间件链 + 动态子智能体并行调度（最多 3 并行，15min 超时）
- Docker/K8s 隔离沙箱执行（AIO Sandbox）
- 跨会话持久记忆 + 可插拔 Skill 系统（10+ 内置技能）
- flash/fast/standard/pro/ultra 五模式自主编排
- 原生适配飞书/Telegram/Slack，无需公网 IP
- 适用于 >30min 长时自主任务
- 外部编排，不替代 Superpowers 内部子 Agent

## 证据

- [GitHub bytedance/deer-flow](https://github.com/bytedance/deer-flow)
- v3.1(2026-05-02) LangGraph 1.0 架构；v2.0(2026-02-27) 发布当日 GitHub Trending #1
- 50K+ Stars / 5800+ Forks；MIT License

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

## v10.3 增量

- Delta 刷新：v2.0 → v3.1；Stars 50K+；中间件 9 → 11 层
- 模式扩展：四模式 → 五模式（+fast）
- 沙箱升级：AIO Sandbox（本地/Docker/K8s 三模式）
- 决策不变：L3 可选，与 workstream 互斥
