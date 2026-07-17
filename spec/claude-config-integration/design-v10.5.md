# .claude 配置集成设计 v10.5

> 状态: **已完成** 2026-07-17 | 调研: `docs/research/` v10.5 | 计划: `docs/superpowers/plans/2026-07-17-v10.5-optimization.md`

## 相对 v10.4 增量

| 领域                | v10.4                                 | v10.5                                |
| ------------------- | ------------------------------------- | ------------------------------------ |
| Understand-Anything | L3 按需（catalog）                    | **removed**（Q5）                    |
| 探索链              | codegraph → cbm(L4) → Grep（UA 可选） | codegraph → cbm(L4) → Grep → Read    |
| Cursor 工具纪律     | explore_router 仅 nudge               | **soft_block**（不可用则降级 nudge） |
| MCP 常驻            | 文档写 5；实际含 chrome-devtools 漂移 | **纠偏常驻 5**                       |
| 调研                | 29 active                             | **28 active + 1 removed**            |
| 上游版本            | 钉 v10.4                              | 文档跟踪漂移；**不自动升**（R14）    |

## 访谈共识（Q1–Q5）

见计划 [`docs/superpowers/plans/2026-07-17-v10.5-optimization.md`](../../docs/superpowers/plans/2026-07-17-v10.5-optimization.md)。

## 设计原则

继承企业级骨架既有原则（五柱×五阶段×三横切、L0–L3、R12–R19）。v10.5 增量：

- **P13** UA 出骨架后，架构/onboarding 缺口只由 cbm+codegraph 填补，禁止再引入第三图谱产品而不经访谈。
- **P14** Cursor 工具纪律：违规须暴露（deny 或 nudge），禁止静默绕过 R17。

## Phase 落地

1. Wave1 docs — ✅
2. Wave2 本设计 + 优化计划 — ✅
3. Wave3 MANIFEST/CORE/MCP/Guard/UA 清除/sync — ✅

**验收**：`validate_config.py` ALL CHECKS PASSED；Guard regression 25/25；`.mcp.json` 常驻 5；`explore.enforce_mode=soft_block`。
