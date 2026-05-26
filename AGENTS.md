# AGENTS.md — 跨编辑器 autodiscovery 镜像

> 详规 → `~/.claude/CLAUDE.md` + `SPEC.md` + `MANIFEST.yaml`
> 来源：obra/superpowers + GSD-redux + Fission-AI/OpenSpec + garrytan/gstack + thedotmack/claude-mem

## P0 Skill

using-superpowers | brainstorming | verification-before-completion | systematic-debugging

## 任务路由

Bug/Issue → triage → systematic-debugging | brainstorming

Mattpocock 精选：triage | improve-codebase-architecture

## 非简单任务

brainstorming → writing-plans → executing-plans → verification-before-completion

## Tool-First

MANIFEST 查 owner → skill → catalog → agent → hook/MCP

## 审查路由（gstack）

```
所有变更        → Eng Review（必须）
产品/新功能     → + CEO Review
UI/UX 变更      → + Design Review
安全敏感变更    → + Security Review
infra/配置      → CEO Review 可跳过
```

| 角色 | Agent | 位置 |
|------|-------|------|
| Eng Reviewer | eng-reviewer | agents/ + catalog/agents/ |
| CEO Reviewer | ceo-reviewer | agents/ + catalog/agents/ |
| Designer | designer | agents/ + catalog/agents/ |
| QA | qa | agents/ + catalog/agents/ |
| Security | security-reviewer | agents/ + catalog/agents/ |

## Token

Shell: RTK | 回复: caveman-compress

## 路径

skills/ agents/ rules/ | catalog/skills/ catalog/agents/

## 新增角色

cso | sre | release-engineer | product-manager | design-engineer | performance-engineer | doc-writer

## 语言

除代码外，优先中文。
