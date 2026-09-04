---
description: 按 gstack 路由规则执行多角色审查
---

# /review — gstack 多角色审查

按变更类型自动路由审查角色。**路由规则 SSOT → `skills/agent-collaboration`，本命令不复写**。

执行：

1. `git diff --name-only HEAD~1`（或指定 base）获取变更文件清单
2. Read `skills/agent-collaboration` → 按审查路由委派（所有变更 eng-reviewer 必审；产品→+ceo-reviewer；UI/UX→+designer+dx-reviewer；安全→+security-reviewer）
3. 汇总输出：各角色结论 + 最终建议

全局权威：`~/.claude/agents/`。
