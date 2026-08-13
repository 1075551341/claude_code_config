---
description: L3 深度调研（Firecrawl+Exa+交叉验证，Read skills/deep-research）
---

# /deep-research — 深度调研

L3 调研入口：**Read `skills/deep-research/SKILL.md`**（工具链、L1→L2→L3 三档升级决策、验证协议 SSOT；v11.1 薄壳化，分级表不复写）。

前置：claude-mem search（R18）；项目内代码用 codegraph_explore（非本链）。

输出要求：关键结论 ≥2 个独立来源交叉验证；标注时效性与可信度；矛盾信息显式列出；禁止仅凭训练数据断言。

| 类型               | 路由                   |
| ------------------ | ---------------------- |
| 网页/竞品/趋势调研 | 本命令 + Firecrawl/Exa |
| 项目内代码结构     | codegraph_explore      |
| 库/API 文档        | Context7               |
