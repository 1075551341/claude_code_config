# GSD 能力缺口（v10 — 仅文档）

> 访谈决策：**不实现** `/gsd-forensics`、`/gsd-resume-work` 命令；保留轻量 `workstream-management` + `stop-session-summary`。

## 未采纳（参考 open-gsd）

| 能力 | 说明 | 本地替代 |
|------|------|----------|
| `/gsd-forensics` | 会话失败根因、工具链回放 | `stop-session-summary` + claude-mem `search` |
| `/gsd-resume-work` | 跨会话恢复 GSD 工作流状态 | `@session-digest.md` + `STATE.md` / workstream 制品 |
| GSD manager dashboard | 并行 workstream 可视化 | `docs/ADR/2026-06-10-gsd-workstreams-evaluation.md` |

## 已采纳

- GSD **70% 逻辑断点**（任务边界，非强制压缩）→ `rules/CORE.md`、`RUNTIME_PLAYBOOK.md`
- `/workstream` → `skill/workstream-management`（MANIFEST excludes deer-flow 互斥）

## 复评估触发

- 并行 ≥3 workstream 且频繁中断恢复
- 用户显式要求 GSD 原生 forensics/resume
