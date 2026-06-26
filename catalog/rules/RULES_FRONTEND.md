---
description: 前端代码开发时启用
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

# 前端规则（专用）

> 配合核心规则使用，仅在前端场景加载。复制到项目 `.claude/rules/frontend.md` 或 `.cursor/rules/frontend.mdc` 后由 `paths` 自动匹配。

## 技术选型

```
需求复杂度      →  推荐方案
─────────────────────────────────
静态/简单交互   →  原生 HTML/CSS/JS
组件化 SPA      →  React（默认）/ Vue
轻量嵌入场景    →  Web Components
```

不为框架而框架，选最轻量够用的。

## 代码质量工具分工（ESLint / Prettier / Stylelint）

> **teoms-web 实践**：三者职责分离。ESLint 管代码异常，Prettier 管格式化，Stylelint 修补样式规范（嵌套空行等 Prettier 不处理的规则）。样式文件由 Prettier 格式化 + Stylelint fix 叠加，须配 `stylelint-config-prettier` 防冲突。

### 职责边界

| 工具 | 职责 | 覆盖范围 | 不做什么 |
|------|------|----------|----------|
| **ESLint** | 代码逻辑与语法异常、Vue/TS 规范 | `.js` `.jsx` `.ts` `.tsx` `.vue` | 缩进/换行等格式化（交给 Prettier） |
| **Prettier** | 格式化 | 上述 + `.json` `.html` `.css` `.less` `.scss` `.md` | 样式语义规范（如嵌套规则前空行） |
| **Stylelint** | 样式规范修补 | `.css` `.less` `.scss` `.vue`（style） | 不替代 Prettier；Vue 保存时不叠加 fix（避免与 template 冲突） |

### 防冲突原则

```
eslint.format.enable = false
eslint-config-prettier + plugin:prettier/recommended   # 关闭 ESLint 与 Prettier 重复规则
stylelint-config-prettier                              # 关闭 Stylelint 与 Prettier 重复规则
prettier.requireConfig = true
vue.format.enable = false                              # 禁用 Volar 内置格式化，统一走 Prettier
```

### 项目配置文件（模板，对齐 teoms-web）

**`.eslintrc.js`**（质量 + `eslint-config-prettier`）

```js
module.exports = {
  root: true,
  parser: 'vue-eslint-parser',
  parserOptions: { parser: '@typescript-eslint/parser', ecmaVersion: 2020, sourceType: 'module' },
  extends: [
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
    'plugin:prettier/recommended',
  ],
};
```

**`prettier.config.js`**（格式化 SSOT；对齐 `templates/lint/.prettierrc.json` v10.3.1）

```js
module.exports = {
  printWidth: 120,
  semi: true,
  tabWidth: 2,
  useTabs: false,
  singleQuote: true,
  trailingComma: 'all',
  arrowParens: 'always',
  bracketSpacing: true,
  bracketSameLine: false,           // 开标签 > 独立成行（v10.3.1+ ESLint 9 flat config 安全）
  singleAttributePerLine: true,     // 多属性每行一个
  vueIndentScriptAndStyle: true,    // Vue SFC script/style 块缩进一级
  quoteProps: 'as-needed',
  proseWrap: 'never',
  htmlWhitespaceSensitivity: 'ignore',  // >/文本/</tag> 各自独占一行（勿用 strict）
  endOfLine: 'lf',
  embeddedLanguageFormatting: 'auto',
};
```

**`stylelint.config.js`**（规范修补；配合 `stylelint-config-prettier`）

```js
module.exports = {
  root: true,
  plugins: ['stylelint-order'],
  customSyntax: 'postcss-less',
  extends: ['stylelint-config-standard', 'stylelint-config-prettier'],
  rules: {
    'rule-empty-line-before': ['always', { ignore: ['after-comment', 'first-nested'] }],
    'selector-pseudo-element-no-unknown': [true, { ignorePseudoElements: ['v-deep'] }],
  },
  ignoreFiles: ['**/*.js', '**/*.jsx', '**/*.tsx', '**/*.ts'],
};
```

### VS Code 保存策略（`.vscode/settings.json`）

**全局**

```json
{
  "editor.tabSize": 2,
  "editor.formatOnSave": true,
  "editor.formatOnSaveMode": "file",
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" },
  "eslint.enable": true,
  "eslint.format.enable": false,
  "eslint.validate": ["javascript", "javascriptreact", "typescript", "typescriptreact", "vue"],
  "stylelint.enable": true,
  "stylelint.validate": ["css", "less", "scss", "vue"],
  "prettier.enable": true,
  "prettier.requireConfig": true,
  "vue.format.enable": false,
  "files.eol": "\\n",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true
}
```

**按语言叠加（css/less/scss：Prettier 格式化 + Stylelint fix；勿全局开 stylelint fix）**

```json
{
  "[vue]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[javascript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[typescript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[css]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": { "source.fixAll.stylelint": "explicit" }
  },
  "[less]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": { "source.fixAll.stylelint": "explicit" }
  },
  "[scss]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": { "source.fixAll.stylelint": "explicit" }
  }
}
```

**保存时执行顺序**

```
JS/TS/Vue/JSON/HTML:
  1. ESLint fix
  2. Prettier format

CSS/Less/Scss:
  1. Stylelint fix（嵌套空行等规范）
  2. Prettier format（缩进/引号）

Vue 单文件（编辑器内）:
  保存 → ESLint + Prettier；Stylelint 仅诊断
  提交 → lint-staged 跑 stylelint --fix
```

### lint-staged 顺序（`package.json`）

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.vue": ["eslint --fix", "prettier --write", "stylelint --fix"],
    "*.{scss,less,styl,html}": ["stylelint --fix", "prettier --write"],
    "*.md": ["prettier --write"]
  }
}
```

原则：**先 lint fix（语义/规范）→ 再 prettier（格式）**。

### Vue 模板格式预期

```vue
<!-- 短标签可单行；属性超 printWidth 时多行，但闭合标签必须完整 -->
<Button class="mr-2" type="default" @click="fn">确定</Button>

<!-- 多属性时：> 独立一行（Prettier 默认）；文本独立一行 -->
<Button
  class="mr-2"
  type="default"
  @click="handlerConfig"
  v-if="hasPermission('module:action')"
>
  设置
</Button>
```

禁止出现：`>设置</Button` + 下一行 `>`（`htmlWhitespaceSensitivity: 'strict'` 导致）。

### 推荐扩展（`.vscode/extensions.json`）

- `Vue.volar`
- `dbaeumer.vscode-eslint`
- `esbenp.prettier-vscode`
- `stylelint.vscode-stylelint`

### 推荐 devDependencies

```bash
pnpm add -D eslint eslint-plugin-vue @typescript-eslint/parser @typescript-eslint/eslint-plugin \
  eslint-config-prettier eslint-plugin-prettier \
  prettier stylelint stylelint-config-standard stylelint-config-prettier stylelint-order postcss-less
```

### 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| `</Button>` 拆成两行 | `htmlWhitespaceSensitivity: 'strict'` | 改为 `'ignore'` |
| `Insert ⏎` 红字（prettier/prettier） | legacy `bracketSameLine: true` 与 eslint-plugin-prettier 冲突 | v10.3.1+ 用 ESLint 9 flat config + eslint-config-prettier（非 plugin 模式），`bracketSameLine: false` 安全无冲突；legacy 项目仍按旧警告处理 |
| Less 嵌套选择器红波浪线 | Stylelint `rule-empty-line-before` 缺空行 | 保存（stylelint fix）或 `pnpm exec stylelint --fix` |
| 保存后缩进仍乱 | 未设 `defaultFormatter` 或无 `prettier.config.js` | `prettier.requireConfig: true` + 补配置 |
| Vue 模板被反复改坏 | 全局 `source.fixAll.stylelint` 与 Prettier 同时 fix | 仅 css/less/scss 语言块启用 stylelint fix |

### Agent 改代码时

- `.vue` / `.ts` / `.js`：遵守 ESLint；格式以 Prettier 为准
- `.less` / `.css` / `.scss`：嵌套规则间补空行；保存顺序 stylelint → prettier
- 完成前：对相关文件确认 ESLint / Stylelint 无新增 error

## 组件规范（React 示例）

### 文件结构

```
ComponentName/
  ├── index.tsx          # 导出入口
  ├── ComponentName.tsx  # 主逻辑
  ├── ComponentName.css  # 样式（可选，优先 CSS Modules）
  └── README.md          # 复杂组件必须提供
```

### 组件注释模板

```tsx
/**
 * @组件 ComponentName
 * @描述 [一句话说明用途]
 * @Props
 *   - propA {string}  说明，默认值
 *   - propB {boolean} 说明，默认 false
 * @示例 <ComponentName propA="value" />
 * @注意 [副作用、依赖、限制]
 */
```

## 样式规范

- CSS Variables 统一 Token（颜色 / 间距 / 字号）
- 响应式：移动优先（`min-width` 断点）
- 命名：BEM 或 CSS Modules，避免全局污染
- 动画：CSS 优先；复杂交互用 Motion / GSAP

## 性能检查

- [ ] 图片懒加载 + WebP 格式
- [ ] 代码分割（动态 `import()`）
- [ ] 避免不必要重渲染（`memo` / `useMemo` / `useCallback`）
- [ ] 关键资源预加载（`<link rel="preload">`）
- [ ] 虚拟滚动（列表 > 500 项）

## 安全

> 详见 `RULES_SECURITY.md`（XSS防护、CSP配置、敏感信息处理等完整覆盖）

## 何时必须写 README

```
① Props > 5 个
② 含异步逻辑 / 状态机
③ 依赖特定 Context / Store
④ 对外暴露 ref 方法

README 最小内容：功能描述 + Props 表 + 使用示例 + 注意事项
```

## 兼容性

- 默认目标：最近 2 个主流浏览器版本
- IE / 特殊兼容需求：任务开始前明确声明
