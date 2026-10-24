---
name: receiving-code-review
description: 薄壳·处理审查结论→verification-before-completion「集中改齐」（覆盖上游同名）
triggers: [接收代码审查反馈, 处理审查意见]
layer: supplement
source: obra/superpowers
disable-model-invocation: true
loading_tier: L3
---

# 接收审查反馈（薄壳）

收到审查结论后：先逐条核实（不盲从、不辩护）→ 汇总完整清单 → 派一次 `change-implementer` 集中改齐 → 验证 → 刷图 → **全新**开审。整轮判定与轮次上限见 **`skills/verification-before-completion/SKILL.md`「独立审查」节**。

保留原因：本地同名技能覆盖 superpowers 插件上游版本，避免两套审查流程互博。
