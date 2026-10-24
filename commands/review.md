---
description: 派发一轮全新独立审查（任务完成的必经门）
---

# /review — 独立审查

每个任务完成前必须有一轮全新独立审查 PASS。政策 SSOT → `skills/verification-before-completion/SKILL.md`「独立审查」节；路由 → `rules/AGENTS.md`（派生自 `config/workflow.yaml`）。本命令不复写。

执行：

1. 确认验证证据已贴、审查前刷图已在 last_edit 之后完成
2. `git diff --name-only <起点 tip>`（或指定 base）列出变更；按路由选审查者（eng-reviewer 必派），同一消息并行全新 `Task`
3. prompt 带原始要求原文、起点 tip、变更清单、主会话已观察到的测试/validate/check 输出原文与相对起点的行为差异（审查者多为只读，凭此核对原功能保持）；要求七维 + 两道门各一行：`- 符合预期要求：通过|不通过（证据：…）`、`- 原功能保持：通过|不通过（证据：…）`
4. 汇总：全部干净 PASS → 任务完成；否则汇总完整清单 → `change-implementer` 集中改齐 → 再验证 → 下一轮全新开审（上限 `review.max_rounds`，用尽 = BLOCKED）
