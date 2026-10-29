---
description: 站立完成目标（两道门：符合预期要求 + 原功能保持）
---

# /goal — 默认完成目标

本命令只复述主干里的**站立目标**，与 `review.pass_requires` 同一两道门。不是第三道软门，也不另建 Stop hook。

**SSOT**：`config/workflow.yaml` `completion.standing_goal`（改完 `python scripts/workflow.py render`）。完成定义与机械门仍是 `review.pass_requires` / `hooks/_lib/r20_replay.py` `review_bars_ok`。

<!-- spine:standing-goal -->
**站立目标**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：`/goal` 复述完成两道门，不是第三道门，也不另建 Stop hook。

- 所有修改符合预期要求
- 且原功能保持不变

PASS 定义（与 `review.pass_requires` 相同）：
  1. **符合预期要求**：每项改动都对应原始要求 / 验收标准；逐条无遗漏；无破坏要求的范围外改动（满足 + 遗漏 + 错改 维）。证据：原始要求逐条 → 对应改动或明确的反驳/弃权理由。
  2. **原功能保持**：起点 tip 上既有的预期行为全部保持，无静默回归；有意的行为变更逐条显式列出并对应原始要求（原功能 维）。证据：相关测试 / validate / check 脚本的观察输出 + 相对起点 tip 的行为差异说明。
<!-- /spine:standing-goal -->
