---
name: design-pipeline
description: 设计管线，从探索到生产。shotgun 生成多方案 → 选定 → HTML 转化。
layer: supplement
source: garrytan/gstack
---

# Design Pipeline

## 触发
- 手动：`/design-shotgun` → `/design-html`

## 流程

### Phase 1: 探索 (shotgun)
1. 生成 4-6 个 AI mockup 变体
2. 在浏览器并排展示
3. 收集反馈（"更多留白"/"更粗标题"）
4. 品味记忆学习偏好
5. 迭代直到满意

### Phase 2: 实现 (html)
1. 读取选定的 mockup
2. 检测框架（React/Svelte/Vue）
3. 生成生产级代码
4. 确保：文本回流、高度自适应、零依赖
5. 输出可交付代码

## 品味记忆
跨会话学习设计偏好，5%/周衰减
