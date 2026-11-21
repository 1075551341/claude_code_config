# DESIGN.md 使用规范

> 用于 UI/设计项目的前端 token 标准化。本文件是规范说明；项目需要时在项目根创建自己的 `DESIGN.md`。

## 何时创建

- 新建 UI 项目 / 落地页 / Dashboard / 设计系统。
- 需要跨组件一致的视觉语言（颜色/字体/间距/动效）。
- 多个协作者或 AI Agent 需要统一设计 token。

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

1. **Token 优先**：组件引用 token（`var(--color-primary)`），不硬编码色值。
2. **单一来源**：项目根 `DESIGN.md` 是设计系统 SSOT。
3. **项目内自足**：仅在当前项目内维护实际使用的设计 Token，不在项目文档中跨端或跨全局目录硬引用外部技能路径。
4. **可读性**：`DESIGN.md` 是给人和 AI 共用的「设计系统说明书」，只写实际使用的 token。

## 与工作流的关系

- 设计决策/取舍 → `docs/ADR/`。
- 任务计划 → `spec/<project>/`。
- 本文件只描述视觉 token，不描述流程、工具或 agent。

## 参考

- [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — DESIGN.md 示例。
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — 设计系统生成器。
