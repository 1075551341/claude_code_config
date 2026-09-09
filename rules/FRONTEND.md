---
trigger: glob
description: 前端代码开发时启用。触发：vue/tsx/jsx/css/html（不含裸 js）
globs: "**/*.{vue,jsx,tsx,css,less,scss,html}"
---

# 前端规则（栈无关）

> 配合核心规则使用，仅在前端文件 glob 匹配时加载。
> 项目级覆盖（含具体框架 ESLint/Vue/React 模板）→ `catalog/rules/`，禁止把某一仓库的栈当全局默认。
> 工具链地板（Node 22+ / pnpm 11）→ `config/toolchain.yaml`。缺工具 BLOCKED，禁止静默回退 npm。

## 技术选型

```
需求复杂度      →  推荐方案
─────────────────────────────────
静态/简单交互   →  原生 HTML/CSS/JS
组件化 SPA      →  项目已有栈；新项目选最轻量够用的
轻量嵌入场景    →  Web Components
```

不为框架而框架。

## 代码质量工具分工

职责分离：Linter 管逻辑/语法异常；Formatter 管格式；Stylelint 管样式语义（嵌套空行等 Formatter 不处理的规则）。

| 工具 | 职责 | 不做什么 |
|------|------|----------|
| Linter | 逻辑与语法、框架规范 | 缩进/换行等格式化 |
| Formatter | 格式化 | 样式语义规范 |
| Stylelint | 样式规范修补 | 不替代 Formatter |

防冲突：关闭 Linter 的 format 能力；用 prettier 兼容层关掉与 Formatter 重复的规则。项目配置放在仓库内，不在本全局规则复制某一项目的 `.eslintrc`。

原则：**先 lint fix（语义/规范）→ 再 format（格式）**。Agent 改前端文件时遵守项目已有 Linter/Formatter；完成前确认无新增 error。

## 组件规范

### 文件结构（示例）

```
ComponentName/
  ├── index.tsx
  ├── ComponentName.tsx
  ├── ComponentName.css
  └── README.md
```

### 组件注释模板

```
@组件 ComponentName
@描述 [一句话说明用途]
@Props  propA {string} 说明
@示例  <ComponentName propA="value" />
```

## 样式规范

- CSS Variables / Design Token 统一颜色、间距、字号；组件不硬编码色值
- 响应式：移动优先（`min-width` 断点）
- 命名：BEM 或 CSS Modules，避免全局污染

## 性能检查

- [ ] 图片懒加载 + 现代格式
- [ ] 代码分割（动态 `import()`）
- [ ] 避免不必要重渲染

## 安全

> 详见 `rules/SECURITY.md`（XSS、CSP 等）

## 何时必须写 README

```
① Props > 5 个
② 含异步逻辑 / 状态机
③ 依赖特定 Context / Store
④ 对外暴露 ref 方法
```

## 兼容性

- 默认目标：最近 2 个主流浏览器版本
- 特殊兼容需求：任务开始前明确声明

## 设计系统（DESIGN.md 规范，v11 并入原 rules/DESIGN.md）

> 来源：VoltAgent/awesome-design-md | token 定义在项目根 `DESIGN.md`

### 何时创建

- 新建 UI 项目 / 落地页 / Dashboard
- 需要跨组件一致视觉语言

### 结构（YAML frontmatter + Markdown）

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

### 原则

1. **Token 优先** — 组件引用 token，不硬编码色值
2. **单一来源** — 项目根 `DESIGN.md` 为 SSOT
3. **与 skill 配合** — 复杂 UI 可启用 `catalog/skills/ui-ux-pro-max`

模板：`~/.claude/templates/DESIGN.md`｜详解：`docs/DESIGN.md`
