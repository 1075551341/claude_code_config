---
name: design-pipeline
description: 设计管线，从探索到生产。shotgun 多方案→对比板→选定→HTML 转化。吸收 gstack /design-shotgun + /design-html 全流程。
layer: supplement
source: garrytan/gstack + VoltAgent/awesome-design-md
---

# Design Pipeline

> 三阶段：探索(shotgun) → 选定 → 实现(html)。品味记忆跨会话学习。

## 触发
- `/design-shotgun` — 启动探索
- `/design-html` — 将选定方案转代码
- 提及"设计方案"/"多方案对比"/"mockup"

## Phase 1: Shotgun（多方案探索）

1. **生成 4-6 变体**：根据需求描述，GPT Image 生成不同风格的 mockup
2. **并排对比板**：浏览器中打开所有变体，支持并排检视
3. **收集反馈**：自然语言反馈（"更多留白"/"去掉渐变"/"标题更大"）
4. **品味记忆**：`gstack-taste-update` 持久化偏好，5%/周衰减，未来生成自动偏置
5. **迭代**：重复 1-4 直到选定满意方案
6. **选定输出**：最终选定的 mockup 传给 Phase 2

## Phase 2: HTML（生产级实现）

1. **读取 mockup**：解析选定方案的视觉结构
2. **检测框架**：自动识别项目使用 React/Svelte/Vue，输出对应格式
3. **Pretext 布局**：30KB 零依赖，文本可回流、高度自适应、布局动态计算
4. **智能路由**：根据设计类型（landing/dashboard/form/card）选择最优 API 模式
5. **输出**：可交付的生产级代码，非 demo

## Phase 3: Token 验证（DESIGN.md 对齐）

- 组件引用 design token，不硬编码色值
- CI 检查：`grep -r "#[0-9a-fA-F]{6}" components/` 应返回空
- 来源：VoltAgent/awesome-design-md

## 品味记忆
- 跨会话学习设计偏好
- `gstack-taste-update` 写入 ~/.gstack/taste/
- 5%/周衰减，长期偏好固化
