---
description: UI/设计项目规范。触发：DESIGN.md、设计系统、design token、UI 规范。
alwaysApply: false
layer: supplement
source: VoltAgent/awesome-design-md + nextlevelbuilder/ui-ux-pro-max-skill
---

# DESIGN.md 使用规范

> 来源：VoltAgent/awesome-design-md | token 定义在项目根 `DESIGN.md`

## 何时创建

- 新建 UI 项目 / 落地页 / Dashboard
- 需要跨组件一致视觉语言

## 结构（YAML frontmatter + Markdown）

```yaml
---
design_system:
  colors:
    primary: "#..."
    background: "#..."
  typography:
    heading: "..."
    body: "..."
  spacing:
    unit: 4
  motion:
    duration: 200ms
---
```

## 原则

1. **Token 优先** — 组件引用 token，不硬编码色值
2. **单一来源** — 项目根 `DESIGN.md` 为 SSOT
3. **与 skill 配合** — 复杂 UI 可启用 `catalog/skills/ui-ux-pro-max`

## 模板

`~/.claude/templates/DESIGN.md`
