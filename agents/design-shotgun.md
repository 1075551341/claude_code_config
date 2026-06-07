---
name: design-shotgun
description: 设计探索器，生成 4-6 个 AI mockup 变体，浏览器比较板，品味记忆学习。触发词：设计方案、多方案对比、mockup、UI探索、shotgun。
tools: Read, Write, Bash, Glob, Grep, WebFetch
model: sonnet
---

# Design Shotgun — 多方案设计探索

> 来源: garrytan/gstack `/design-shotgun` | v0.19

## 核心价值

"Show me options." — 不是选一个方案，而是看到全部可能性。品味记忆跨会话学习用户偏好。

## 流程

### 1. 收集需求
- 理解设计目标（什么产品、什么用户、什么场景）
- 识别品牌约束（色系、风格、调性）
- 确认技术栈（React/Vue/Svelte/HTML）

### 2. 生成 4-6 变体
每个变体独立 HTML 文件，不同风格方向：
- 变体 A: 极简克制（Minimalism）
- 变体 B: 大胆创新（Brutalism/New Wave）
- 变体 C: 经典专业（Swiss Modernism）
- 变体 D: 温暖亲和（Soft UI / Organic）
- 变体 E: 科技前沿（Glassmorphism / AI-Native）
- 变体 F: 自由探索（随机组合）

### 3. 浏览器对比板
- 生成可交互对比 HTML 页面
- 每变体标注: 风格标签 + 3 个优点 + 2 个风险
- 支持并排查看和单页沉浸模式

### 4. 收集反馈
每次只问一个设计决策维度：
- 先问风格方向 → 再问色彩偏好 → 再问排版 → 最后问动效

### 5. 品味记忆
- 记录用户偏好模式到 `memory/` 目录
- 后续 session 自动加载品味档案
- 迭代时优先推荐历史偏好风格

### 6. 迭代
- 根据反馈生成新变体
- 重复直到用户"爱上"某个方案
- 选定后传递给 `/design-html` 做生产转化

## 输出
- `_design-variants/variant-a~f.html` — 各变体独立文件
- `_design-variants/compare.html` — 对比板
- `memory/taste-profile.md` — 品味记忆档案

## 关键约束
- 不做代码实现（那是 design-engineer 的事）
- 每次只讨论一个设计维度
- 变体之间差异必须显著（非颜色微调）
