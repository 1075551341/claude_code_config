---
description: TypeScript 开发时按需加载
alwaysApply: false
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript 规则（lazy-load 示例）

> 完整规则见 `~/.claude/catalog/rules/RULES_TYPESCRIPT.md`，复制到项目后按需编辑。

## 要点

- `strict: true`
- 优先 interface + 泛型约束
- 禁止 `any`（边界除外并注释）
- 异步必须显式错误处理

## 启用方式

1. 复制 `catalog/rules/RULES_TYPESCRIPT.md` → 项目 `.claude/rules/typescript.md`
2. 保留 `paths:` frontmatter 匹配 `*.ts` / `*.tsx`
