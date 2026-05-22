---
name: ui-ux-pro-max
description: UI/UX 设计智能搜索。触发词：UI设计、UX、设计系统、landing page、dashboard 设计。
---

# UI/UX Pro Max（catalog 按需）

> 来源：nextlevelbuilder/ui-ux-pro-max-skill | 全局不加载，按需复制到项目

## 使用方式

1. 项目根创建 `DESIGN.md`（模板：`~/.claude/templates/DESIGN.md`）
2. 启用 `catalog/skills/frontend-design` 或官方 `frontend-design` plugin
3. 复杂 UI 任务配合 `rules/DESIGN.md`

## 能力

- 设计 token / 配色 /  typography 决策
- 落地页、Dashboard、Admin 布局模式
- 与 `ce-frontend-design` / `frontend-design` skill 互补

## 复制到项目

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project . --skill ui-ux-pro-max --skill frontend-design
```
