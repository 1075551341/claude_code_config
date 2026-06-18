# Agents 索引

> 自动生成 | 源：`agents/` | v10.2

## 核心 7

- [planner](agents/planner.md) — 薄编排：调用 writing-plans skill
- [code-explorer](agents/code-explorer.md) — 只读代码探索
- [code-reviewer](agents/code-reviewer.md) — 代码审查（不改代码）
- [build-error-resolver](agents/build-error-resolver.md) — 构建/编译/类型错误修复
- [architect](agents/architect.md) — 系统架构设计
- [spec-reviewer](agents/spec-reviewer.md) — 规格/计划文档审查
- [agentic-orchestrator](agents/agentic-orchestrator.md) — 多 Agent 并行编排

## gstack 审查 (6)

- [eng-reviewer](agents/eng-reviewer.md) — 工程审查（所有变更必须通过）
- [ceo-reviewer](agents/ceo-reviewer.md) — 产品决策审查
- [designer](agents/designer.md) — UI/UX 审查
- [dx-reviewer](agents/dx-reviewer.md) — 开发体验审查
- [qa](agents/qa.md) — 质量保障审查
- [security-reviewer](agents/security-reviewer.md) — 安全审查（OWASP）

## gstack 补全 (6)

- [cso](agents/cso.md) — OWASP Top 10 + STRIDE 威胁建模
- [sre](agents/sre.md) — Canary 监控、部署后验证
- [release-engineer](agents/release-engineer.md) — 同步main、测试、推送、开PR
- [product-manager](agents/product-manager.md) — 六问框架产品分析
- [design-engineer](agents/design-engineer.md) — Mockup to HTML/CSS 转化
- [performance-engineer](agents/performance-engineer.md) — Core Web Vitals 基准

## gstack v0.19 扩展 (4)

- [design-shotgun](agents/design-shotgun.md) — 4-6个AI mockup变体+浏览器比较板
- [pair-agent](agents/pair-agent.md) — 多AI Agent浏览器共享协作
- [land-and-deploy](agents/land-and-deploy.md) — 一键部署（approved PR to production）
- [ios-specialist](agents/ios-specialist.md) — iOS 专用审查

## gstack v0.19 跨模型 (1)

- [codex-reviewer](agents/codex-reviewer.md) — 跨模型独立审查（发现Claude盲点）

## 补全 (1)

- [doc-writer](agents/doc-writer.md) — 更新文档匹配代码变更
