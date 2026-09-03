# Agents 索引

> 自动生成 | 源：`agents/` | v11.4.13（17 全量；catalog 变体见 `catalog/agents/`）

## 核心 7

- [planner](agents/planner.md) — 薄编排：调用 writing-plans skill
- [code-explorer](agents/code-explorer.md) — 只读代码探索
- [code-reviewer](agents/code-reviewer.md) — 代码审查（不改代码）
- [build-error-resolver](agents/build-error-resolver.md) — 构建/编译/类型错误修复
- [architect](agents/architect.md) — 系统架构设计
- [spec-reviewer](agents/spec-reviewer.md) — 规格/计划文档审查
- [agentic-orchestrator](agents/agentic-orchestrator.md) — 多 Agent 并行编排

## gstack 审查 6

- [eng-reviewer](agents/eng-reviewer.md) — 工程审查（所有变更必须通过）
- [ceo-reviewer](agents/ceo-reviewer.md) — 产品决策审查（含六问框架要点）
- [designer](agents/designer.md) — UI/UX 审查
- [dx-reviewer](agents/dx-reviewer.md) — 开发体验审查
- [qa](agents/qa.md) — 质量保障审查
- [security-reviewer](agents/security-reviewer.md) — 安全审查（快速模式 + 深度模式 OWASP Top 10/STRIDE，v11 并入原 cso）

## 补全 3

- [sre](agents/sre.md) — Canary 监控、部署后验证
- [doc-writer](agents/doc-writer.md) — 更新文档匹配代码变更
- [change-implementer](agents/change-implementer.md) — 落实修改（审查者不改代码）

## 跨模型 1

- [codex-reviewer](agents/codex-reviewer.md) — 跨模型独立审查（发现 Claude 盲点）

## v11 变更（原全局 → 去向）

| 原 agent | 去向 |
| --- | --- |
| cso | 并入 `agents/security-reviewer.md`（深度模式） |
| release-engineer | 并入 `skills/ship/SKILL.md` |
| product-manager | 六问框架并入 `catalog/skills/office-hours/` |
| design-engineer | 并入 `skills/design-pipeline/SKILL.md`（Phase 2） |
| design-shotgun / pair-agent / ios-specialist / land-and-deploy / performance-engineer | 降级 `catalog/agents/`（按需复制进项目） |
