# ADR-001: v8.1 → v9.0 配置集成

状态: 已采纳
日期: 2026-06-10

## 背景

对 28 个仓库全量分析（见 `docs/REPO_ANALYSIS.md`），识别五柱骨架完整但存在 workstreams、ADR、DX review、GateGuard、codegraph 优先路由等缺口。

## 决策

1. **R17**：`codegraph_explore` 提升为代码探索首选，Grep 作 fallback
2. **R18**：claude-mem 三层检索工作流正式化，先于重复文件读取
3. **GateGuard**：`stop-context-monitor` + 增强 `pre-suggest-compact`（tool loop / scope creep）
4. **dx-reviewer**：补充开发体验审查维度（TTHW / 摩擦点 / 魔法时刻）
5. **workstreams**：轻量 `workstream-management` skill + git worktrees（非完整 GSD 外部依赖）
6. **ADR**：`docs/ADR/` + `adr-management` skill
7. **OpenSpec**：`rules/OPENSPEC.md` 规范 delta-spec 用法
8. **codegraph 增量同步**：`post-codegraph-sync` hook（变更后自动 sync）

## 后果

正面：
- Token 效率提升（探索 -47%、记忆去重）
- 骨架更清晰，缺口补齐，防互博 MANIFEST 归属明确

负面：
- hooks 数量略增（+2），需 validate_config 通过
- workstreams 为轻量实现，完整 GSD workstreams 待 P3 评估（T28）

## 替代方案

- 保持 v8.1 不变 — **拒绝**（有明确可测量缺口）
- 引入完整 GSD CLI 依赖 — **暂缓**（token/依赖成本待评估）
