# AGENTS.md — 跨编辑器 autodiscovery 镜像

> 详规 → `~/.claude/CLAUDE.md` + `SPEC.md` + `MANIFEST.yaml`

## P0 Skill

using-superpowers | brainstorming | verification-before-completion | systematic-debugging

## 非简单任务

brainstorming → writing-plans → executing-plans → verification-before-completion

## Tool-First

MANIFEST 查 owner → skill → catalog → agent → hook/MCP

## 审查路由（gstack）

```
所有变更        → Eng Review (必须)
产品/新功能     → + CEO Review
UI/UX 变更      → + Design Review
安全敏感变更    → + Security Review
infra/配置      → CEO Review 可跳过
```

| 角色 | Agent | 位置 |
|------|-------|------|
| Eng Reviewer | eng-reviewer | catalog/agents/ |
| CEO Reviewer | ceo-reviewer | catalog/agents/ |
| Designer | designer | catalog/agents/ |
| QA | qa | catalog/agents/ |
| Security | security | catalog/agents/ |

## Token

Shell: RTK | 回复: caveman-compress

## 路径

skills/ agents/ rules/ | catalog/skills/ catalog/agents/

## 语言

除代码外，优先中文。
