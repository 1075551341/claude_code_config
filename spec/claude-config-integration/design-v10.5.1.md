# .claude 配置集成设计 v10.5.1

> 状态: **已完成** 2026-07-17 | 调研: `docs/research/` v10.5.1 | 计划: `docs/superpowers/plans/2026-07-17-v10.5.1-optimization.md`

## 相对 v10.5 增量

| 领域     | v10.5           | v10.5.1                                                    |
| -------- | --------------- | ---------------------------------------------------------- |
| 调研     | 全量卡片 v10.5  | 分层 delta 刷新；优点→落点矩阵                             |
| cbm      | L4 按需（文档） | **场景强制**（未用 → DONE_WITH_CONCERNS）；仍不常驻 Claude |
| 版本号   | 10.5.0          | **10.5.1** patch                                           |
| UA       | removed         | **维持 removed**                                           |
| 上游钉扎 | 文档待评估      | 复核漂移；**仍不自动升**                                   |
| sync     | Wave3 已跑      | 再修 CONTEXT/CORE/MCP 过期                                 |

## 访谈共识（Q1–Q8）

见计划 [`docs/superpowers/plans/2026-07-17-v10.5.1-optimization.md`](../../docs/superpowers/plans/2026-07-17-v10.5.1-optimization.md)。

## 设计原则

继承 v10.5（P13 UA 不出第三图谱；P14 Cursor soft_block）。新增：

- **P15** 「必须用 cbm」= **场景门控强制**，≠ 进程常驻（满足 token 纪律 + 要求 8）。
- **P16** 上游优点默认进调研文档；进运行时须复用既有 concern + R14 评估，禁止顺手升 major。

## Phase 落地

1. Wave1 docs — ✅
2. Wave2 本设计 + 优化计划 — ✅（本文）
3. Wave3 MANIFEST/SPEC/CLAUDE + CORE/CONTEXT/MCP + sync + validate — ✅

**验收**：`validate_config.py` ALL CHECKS PASSED；`.mcp.json` 常驻 5；UA removed；cbm 场景强制已写入 CORE/CONTEXT/MCP。

## 非目标（硬）

不升钉扎、不重装 UA、不扩常驻 MCP、不集成 ruflo、不新增编辑器。
