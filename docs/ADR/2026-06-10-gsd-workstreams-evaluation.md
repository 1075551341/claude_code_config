# ADR-002: GSD Workstreams 轻量 vs 完整实现

状态: 已采纳（轻量方案）
日期: 2026-06-10

## 背景

GSD v1.42.3 提供完整 workstreams（并行分支、manager dashboard、/gsd-resume-work）。本地已有 `workstream-management` skill（T09 轻量实现）。

## 决策

**采用轻量 workstream-management**，不引入完整 GSD CLI 依赖。

理由：
- 核心需求（git worktree 隔离 + `.planning/phases/<name>/`）已覆盖
- 完整 GSD workstreams 增加外部依赖与 token 成本（dashboard、forensics）
- deer-flow 已覆盖外部重型编排场景

## 实现

- `skill/workstream-management` + `skill/using-git-worktrees`
- 命令：`/workstream new|status|list|merge`
- claude-mem 合并时整合各流记忆

## 后果

正面：零额外依赖、MANIFEST 归属清晰、与 OpenSpec 三轨兼容
负面：无 GSD manager dashboard、无 /gsd-forensics（可用 stop-session-summary 部分替代）

## 替代方案

| 方案 | 结论 |
|------|------|
| 完整 GSD workstreams CLI | 暂缓 — P3 按需再评估 |
| 仅 git worktree 无 skill | 拒绝 — 缺流程约束 |
| deer-flow 替代 | 拒绝 — 过重，用于>30min外部编排 |

## 复评触发条件

- 并行流≥3 且频繁冲突
- 需要可视化 dashboard
- open-gsd/gsd-core 提供无依赖轻量 API
