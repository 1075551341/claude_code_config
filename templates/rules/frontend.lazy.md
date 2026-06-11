---
description: 前端开发时按需加载
alwaysApply: false
paths:
  - "**/*.vue"
  - "**/*.jsx"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.css"
  - "**/*.less"
  - "**/*.scss"
  - "**/*.html"
---

# 前端规则（lazy-load 示例）

> 完整规则见 `~/.claude/catalog/rules/RULES_FRONTEND.md`，复制到项目后按需编辑。

## 工具分工（teoms-web 风格）

| 工具 | 职责 |
|------|------|
| ESLint | 代码异常、Vue/TS 规范 |
| Prettier | 格式化（含 Vue 模板；`htmlWhitespaceSensitivity: 'ignore'`，勿设 `bracketSameLine`） |
| Stylelint | 样式规范修补（嵌套空行等；配 `stylelint-config-prettier`） |

## 启用方式

1. 复制 `catalog/rules/RULES_FRONTEND.md` → 项目 `.claude/rules/frontend.md` 或 `.cursor/rules/frontend.mdc`
2. 保留 `paths:` frontmatter 匹配前端文件
3. 项目内补齐 `.eslintrc.js`、`prettier.config.js`、`stylelint.config.js`、`.vscode/settings.json`（见完整规则模板）
