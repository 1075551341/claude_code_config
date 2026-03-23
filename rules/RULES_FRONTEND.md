---
description: 前端代码开发时启用
alwaysApply: false
---

# 前端规则（专用）

> 配合核心规则使用，仅在前端场景加载

## 技术选型

```
需求复杂度      →  推荐方案
─────────────────────────────────
静态/简单交互   →  原生 HTML/CSS/JS
组件化 SPA      →  React（默认）/ Vue
轻量嵌入场景    →  Web Components
```

不为框架而框架，选最轻量够用的。

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

- 禁止 `innerHTML` 直接插入用户数据 → 用 `textContent` 或 DOMPurify
- 敏感信息不写 `localStorage` → 改用 httpOnly Cookie
- CSP 头配置列入上线检查项

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