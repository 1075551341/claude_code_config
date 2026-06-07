# DESIGN.md 使用规范

> 来源：VoltAgent/awesome-design-md | 用于 UI/设计项目的前端 token 标准化
> 本文件为规范说明，非项目级 DESIGN.md。项目需要时创建项目根 `DESIGN.md`。

---

## 何时创建项目 DESIGN.md

- 新建 UI 项目 / 落地页 / Dashboard / 设计系统
- 需要跨组件一致视觉语言（颜色/字体/间距/动效）
- 多个 AI Agent 协作需要统一设计 token

## 标准结构

```yaml
---
design_system:
  colors:
    primary: "#..."
    secondary: "#..."
    background: "#..."
    surface: "#..."
    error: "#..."
    text_primary: "#..."
    text_secondary: "#..."
  typography:
    heading: "Inter, sans-serif"
    body: "Inter, sans-serif"
    mono: "JetBrains Mono, monospace"
    scale:
      xs: "0.75rem"
      sm: "0.875rem"
      base: "1rem"
      lg: "1.125rem"
      xl: "1.25rem"
      2xl: "1.5rem"
      3xl: "1.875rem"
      4xl: "2.25rem"
  spacing:
    unit: 4  # px
  motion:
    duration: "200ms"
    easing: "cubic-bezier(0.4, 0, 0.2, 1)"
  breakpoints:
    sm: "640px"
    md: "768px"
    lg: "1024px"
    xl: "1280px"
---
```

## 核心原则

1. **Token 优先** — 组件引用 token（`var(--color-primary)`），不硬编码色值
2. **单一来源** — 项目根 `DESIGN.md` 为设计系统 SSOT
3. **与 catalog skill 配合** — 复杂 UI 可启用 `catalog/skills/ui-ux-pro-max`
4. **DESIGN.md 是 AI 的"设计系统说明书"** — Claude 通过 Read 获取 token 定义

## 工具链

| 工具 | 触发条件 |
|------|----------|
| `design-pipeline` skill | 设计探索管线（shotgun → 对比板 → HTML转化） |
| `design-shotgun` agent | 生成 4-6 个 AI mockup 变体 |
| `designer` agent | UI/UX 审查，0-10 维度评分 |
| `design-engineer` agent | mockup → 生产级 HTML/CSS |
| `ui-ux-pro-max` catalog skill | 67风格 + 161色板 + 99UX 指南 |

## 参考

- [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — 73 品牌 DESIGN.md 示例
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — 设计系统生成器
- `~/.claude/templates/DESIGN.md` — 设计 token 模板
