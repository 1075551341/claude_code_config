# Agent 路由表

Skills 在 `~/.claude/skills/` | Agents 在 `~/.claude/agents/`

## 可用 Agents

| 名称 | 文件 | 触发场景 |
|------|------|---------|
| Architect | `agents/architect.md` | 系统设计、API 设计、技术选型、重构规划 |
| Eng Reviewer | `agents/eng-reviewer.md` | 代码审查（架构/质量/测试/性能），所有 PR 必须通过 |
| CEO Reviewer | `agents/ceo-reviewer.md` | 产品决策、用户价值、scope 判断（大功能/新特性时用） |
| Designer | `agents/designer.md` | UI 组件、交互设计、视觉规范，纯后端变更跳过 |
| QA | `agents/qa.md` | 测试用例、边界测试、回归测试生成 |
| Debugger | `agents/debugger.md` | 错误根因分析、ECC 上下文捕获 |
| Researcher | `agents/researcher.md` | 技术调研、方案对比、最佳实践收集 |
| Security | `agents/security.md` | OWASP Top 10 / STRIDE 安全审计 |

## 审查路由规则（gstack 智能路由）

```
所有变更 → Eng Review (必须)
产品/新功能/scope变更 → + CEO Review
UI/UX 变更 → + Design Review
安全敏感变更 → + Security Review
infra/配置/cleanup → CEO Review 可跳过
```

## 可用 Skills

| 类别 | Skill | 命令 |
|------|-------|------|
| dev | brainstorm | `/brainstorm` |
| dev | write-plan | `/plan` |
| dev | subagent-execute | `/execute` |
| dev | tdd | 编写测试时自动加载 |
| dev | debug-fix | `/fix` |
| docs | write-spec | `/spec` |
| design | ui-component | 涉及 UI 时 |
| ops | context-save | `/mem-save` |
| ops | context-restore | `/mem-load` |
