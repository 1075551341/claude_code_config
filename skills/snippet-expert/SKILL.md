---
name: snippet-expert
description: 代码片段专家，覆盖JavaScript/ES6及多语言常用模式。触发：快速代码片段、工具函数、常用模式、代码速查、JS代码片段、JavaScript技巧、ES6技巧、代码模式、JS实用代码、JavaScript速查
triggers: [快速代码片段、工具函数、常用模式、代码速查、JS代码片段、JavaScript技巧、ES6技巧、代码模式、JS实用代码、JavaScript速查]
---

# 代码片段专家

## 核心原则

> 提供简洁、可读、即用的代码片段。每个片段 <30 行，附带类型注解和一行说明

## 高频片段库

### JavaScript / TypeScript

| 需求 | 片段 |
|------|------|
| 防抖 | `const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };` |
| 节流 | `const throttle = (fn, ms) => { let last = 0; return (...a) => { const now = Date.now(); if (now - last >= ms) { last = now; fn(...a); } }; };` |
| 深拷贝 | `const deepClone = (obj) => structuredClone(obj);` |
| 去重 | `const unique = (arr) => [...new Set(arr)];` |
| 分组 | `const groupBy = (arr, key) => arr.reduce((acc, item) => ((acc[item[key]] ??= []).push(item), acc), {});` |
| 按键排序 | `const sortBy = (arr, key) => [...arr].sort((a, b) => a[key] > b[key] ? 1 : -1);` |
| 拾取属性 | `const pick = (obj, keys) => keys.reduce((acc, k) => (k in obj && (acc[k] = obj[k]), acc), {});` |
| 睡眠 | `const sleep = (ms) => new Promise(r => setTimeout(r, ms));` |
| 重试 | `const retry = async (fn, n = 3) => { for (let i = 0; i < n; i++) try { return await fn(); } catch (e) { if (i === n - 1) throw e; } };` |
| 范围整数 | `const randInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;` |

### Python

| 需求 | 片段 |
|------|------|
| 防抖 | `debounce = lambda ms: lambda f: wraps(f)(lambda *a, **k: (setattr(debounce, 't', None), (t := getattr(debounce, 't', None)) and t.cancel(), setattr(debounce, 't', Timer(ms/1000, lambda: f(*a, **k))), debounce.t.start())[-1])` |
| 去重 | `unique = lambda lst: list(dict.fromkeys(lst))` |
| 分组 | `def group_by(lst, key): return {k: list(g) for k, g in groupby(sorted(lst, key=key), key=key)}` |
| 拾取 | `pick = lambda d, keys: {k: d[k] for k in keys if k in d}` |
| 扁平化 | `flatten = lambda lst: [x for sub in lst for x in (sub if isinstance(sub, list) else [sub])]` |
| 重试 | `async def retry(fn, n=3): [await fn() for _ in range(n)] # 简化版` |

### CSS

| 需求 | 片段 |
|------|------|
| 居中 | `display: grid; place-items: center;` |
| 文本截断 | `overflow: hidden; text-overflow: ellipsis; white-space: nowrap;` |
| 多行截断 | `display: -webkit-box; -webkit-line-clamp: N; -webkit-box-orient: vertical; overflow: hidden;` |
| 平滑滚动 | `scroll-behavior: smooth;` |
| 毛玻璃 | `backdrop-filter: blur(8px); background: rgba(255,255,255,0.1);` |

### Git

| 需求 | 命令 |
|------|------|
| 撤销上次提交 | `git reset --soft HEAD~1` |
| 修改上次提交 | `git commit --amend` |
| 查看文件历史 | `git log --follow -p <file>` |
| 交互式暂存 | `git add -p` |
| 查找引入bug的提交 | `git bisect start && git bisect bad && git bisect good <commit>` |

## 使用原则

1. 优先使用语言内置/标准库方法
2. 每个片段附带类型注解（TypeScript/Python）
3. 复杂逻辑附一行注释说明
4. 不引入额外依赖
