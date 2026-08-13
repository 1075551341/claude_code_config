---
description: 按 gstack 路由规则执行多角色审查
---

# /review — gstack 多角色审查

按变更类型自动路由审查角色。**路由规则 SSOT → `rules/AGENTS.md`（审查路由 + 何时委派），本命令不复写**（v11.1 薄壳化）。

执行：

1. `git diff --name-only HEAD~1`（或指定 base）获取变更文件清单
2. Read `rules/AGENTS.md` → 按审查路由委派全局 agents（所有变更 eng-reviewer 必审；产品→+ceo-reviewer；UI/UX→+designer+dx-reviewer；安全→+security-reviewer；infra/cleanup 可跳 CEO）
3. 汇总输出：各角色结论（PASS/NEEDS-CHANGES、GO/RETHINK、APPROVED/NEEDS-POLISH、SAFE/RISKS-FOUND）+ 最终建议（可合并 / 需修改）

全局权威：`~/.claude/agents/`；`catalog/agents/` 仅为按需变体库。
