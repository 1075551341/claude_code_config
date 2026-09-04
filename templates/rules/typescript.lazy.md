---
description: TypeScript 开发时按需加载
alwaysApply: false
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript 规则（lazy-load 示例）

> TypeScript 项目约定按需写到项目 `.cursor/rules/`（v12 已删除 catalog 规则库）。

## 要点

- `strict: true`
- 优先 interface + 泛型约束
- 禁止 `any`（边界除外并注释）
- 异步必须显式错误处理

## 启用方式

1. 在项目 `.cursor/rules/typescript.mdc` 写 `paths` 匹配 `*.ts` / `*.tsx`
2. 保留 `paths:` frontmatter 匹配 `*.ts` / `*.tsx`
