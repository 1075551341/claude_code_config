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

> 完整规则见 `~/.claude/rules/FRONTEND.md`，项目级覆盖写到项目 `.cursor/rules/`。

## 工具分工（teoms-web 风格）

| 工具 | 职责 |
|------|------|
| ESLint | 代码异常、Vue/TS 规范 |
| Prettier | 格式化（含 Vue 模板；`htmlWhitespaceSensitivity: 'ignore'`，`bracketSameLine: false`；v10.3.1+ ESLint 9 flat config 安全） |
| Stylelint | 样式规范修补（嵌套空行等；配 `stylelint-config-prettier`） |

## 启用方式

1. 以 `rules/FRONTEND.md` 为源，按需覆盖到项目 `.cursor/rules/frontend.mdc`
2. 保留 `paths:` frontmatter 匹配前端文件
3. 项目内补齐 `.eslintrc.js`、`prettier.config.js`、`stylelint.config.js`、`.vscode/settings.json`（见完整规则模板）
