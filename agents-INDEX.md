# Agents 索引

> 源：`agents/` | v13.0.0（9 全量；agent 不声明 model/effort，继承调用方；catalog 变体见 `catalog/agents/`）

## 阶段角色 2

- [planner](agents/planner.md) — 薄编排：调用 writing-plans skill
- [change-implementer](agents/change-implementer.md) — 落实修改（审查者不改代码）

## 独立审查者 7

- [eng-reviewer](agents/eng-reviewer.md) — 工程 + 代码审查（每个任务必审；PASS 才算完成）
- [ceo-reviewer](agents/ceo-reviewer.md) — 产品决策审查
- [designer](agents/designer.md) — UI/UX 审查
- [dx-reviewer](agents/dx-reviewer.md) — 开发体验审查
- [qa](agents/qa.md) — 质量保障审查
- [security-reviewer](agents/security-reviewer.md) — 安全审查（快速模式 + 深度模式 OWASP Top 10/STRIDE）
- [cross-model-reviewer](agents/cross-model-reviewer.md) — 跨模型独立审查（调用方选与实现者不同的模型）

## v13 变更（原全局 → 去向）

| 原 agent | 去向 |
| --- | --- |
| code-explorer / architect / agentic-orchestrator / build-error-resolver / spec-reviewer / sre / doc-writer | 删除，见 `agents/README.md`「v13 去向」 |
| 原跨模型审查者（v12 名含厂商） | 更名 `cross-model-reviewer` |
