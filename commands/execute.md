---
description: 按已批准计划执行实现（③执行阶段）
---

# /execute — 按计划执行

③执行阶段入口。**正文 SSOT → Read `skills/executing-plans/SKILL.md`**（依赖序执行、失败隔离、状态摘要；R5 同方案≤2 次、R10 简洁、R11 安全），本命令不复写流程（v11.1 薄壳化）。

门控：所有子任务完成 ✓ + 构建/类型/Lint 通过 ✓ + 交叉验证清单通过 ✓（→ ④ `/verify`）。
