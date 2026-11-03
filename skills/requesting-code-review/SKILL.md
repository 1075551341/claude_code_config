---
name: requesting-code-review
description: 薄壳·派发独立审查→verification-before-completion（覆盖上游同名）
triggers: [请求代码审查, 代码审查请求]
layer: supplement
source: obra/superpowers
disable-model-invocation: true
loading_tier: L3
---

# 请求代码审查（薄壳）

派发独立审查的唯一政策在 **`skills/verification-before-completion/SKILL.md`「独立审查」节**（全新开审、审查前刷图、并行路由、prompt 必带项、最多 `review.max_rounds` 轮）。Read 该文件并照做。

保留原因：本地同名技能覆盖 superpowers 插件上游版本，避免两套审查流程互博。
