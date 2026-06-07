# Agents 智能体库

> **全局 24 个**（7 核心 + 5 gstack 审查 + 7 gstack 补全 + 3 gstack v0.19 + 2 扩展）+ **catalog/agents/** 领域库（43）

---

## 核心 7（supplement 层）

| Agent | 预加载 skill | 职责 |
|-------|-------------|------|
| planner | writing-plans | 仅计划，不实现 |
| code-explorer | — | 只读探索 |
| code-reviewer | requesting/receiving-code-review | 审查不改代码 |
| build-error-resolver | systematic-debugging | 构建错误 + 5-Why |
| architect | brainstorming | 架构决策 |
| spec-reviewer | spec-validation | spec 审查 |
| agentic-orchestrator | subagent-driven-development | 多 Agent 并行编排 |

---

## gstack 审查 5（skeleton 层，必须路由）

| Agent | 审查范围 | 触发 |
|-------|----------|------|
| eng-reviewer | 所有变更（必须） | eng review / PR审查 |
| ceo-reviewer | 产品/新功能 | 产品审查 / scope审查 |
| designer | UI/UX 变更 | 设计审查 / UI审查 |
| qa | 测试覆盖 | QA审查 / 测试审查 |
| security-reviewer | 安全敏感变更 | 安全审查 / OWASP |

---

## gstack 补全 7（supplement 层）

| Agent | 职责 | 触发 |
|-------|------|------|
| cso | OWASP + STRIDE 全量审计 | 安全总管 / 威胁建模 |
| sre | canary 监控、部署后验证 | 部署验证 / SRE |
| release-engineer | sync→测试→覆盖→push→PR | /ship |
| product-manager | 六问产品框架 | /office-hours |
| design-engineer | mockup→生产 HTML/CSS | /design-html |
| performance-engineer | Core Web Vitals / 基准 | /benchmark |
| doc-writer | 文档与 release notes | /document-release |

---

## gstack v0.19 新增 3（supplement 层）

| Agent | 职责 | 触发 |
|-------|------|------|
| design-shotgun | 4-6 AI mockup 变体 + 品味记忆 | 设计方案 / 多方案对比 / mockup |
| pair-agent | 多 AI Agent 浏览器共享协作 | 多 Agent 协作 / pair |
| land-and-deploy | 一键部署 PR→production | 部署 / 上线 / land / deploy |

---

## 扩展 2（supplement 层）

| Agent | 职责 | 触发 |
|-------|------|------|
| codex-reviewer | 跨模型独立审查（Codex 视角） | /codex / 跨模型验证 |
| ios-specialist | iOS 专用审查 QA/设计/清理/同步 | iOS 变更（gstack v0.19） |

---

## 调用原则

1. 子 Agent **不继承**会话历史，只注入必要上下文
2. 同一模块 **单一负责**（`MANIFEST.yaml` 查 owner）
3. 无依赖任务 **并行**；失败隔离，不污染其他子目标

## 触发表（source: domengabrovsek/claude）

| 触发 | Agent |
|------|-------|
| 探索/只读/where is | code-explorer |
| 写计划/分解 | planner |
| 构建失败/编译错误 | build-error-resolver |
| 架构/方案 | architect |
| spec 审查 | spec-reviewer |
| 多模块并行 | agentic-orchestrator |
| 代码/PR 审查 | code-reviewer + eng-reviewer |
| 安全审计 | security-reviewer / cso |
| UI/UX | designer / design-engineer |

---

## Catalog（按需）

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project <path> --agent python-reviewer
```

示例：frontend-developer, database-expert …

---

## 互斥

| 场景 | 用 | 不用 |
|------|-----|------|
| 写计划 | agent/planner + writing-plans | planning-expert, pre-task-planner |
| 并行编排 | agentic-orchestrator | planner 并行派发 |
| 跨会话记忆 | claude-mem plugin | context-manager 重复存储 |
| Eng 审查 | eng-reviewer | code-reviewer 替代 eng |
| 发布 | release-engineer + skill/ship | finishing-a-development-branch 单独 ship |

---

## 来源

superpowers + ECC + gstack（cherry-pick）
