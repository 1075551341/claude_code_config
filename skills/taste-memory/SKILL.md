---
name: taste-memory
description: 跨会话设计品味记忆（gstack 互补）。触发：设计偏好、风格选择、minimal/dark/dense。
triggers: [品味, 设计偏好, 风格记忆, taste, minimal, dark mode]
layer: supplement
source: garrytan/gstack
disable-model-invocation: true
loading_tier: L3
---

# 品味记忆（via claude-mem）

不修改 claude-mem 插件，通过 observation 存储设计偏好。

## 记录什么

| 维度 | 示例 |
|------|------|
| 视觉密度 | minimal / dense / spacious |
| 色彩 | dark / light / high-contrast |
| 排版 | 无衬线 / 等宽数据 / 大标题 |
| 交互 | 少点击 / 键盘优先 / 向导式 |
| 否决项 | 拒绝的设计模式（如紫色渐变 AI slop） |

## 工作流

```
1. 用户表达偏好 → 写入 observation（标签: taste-preference）
2. 新 UI 任务前 → claude-mem search "taste-preference"
3. designer / design-shotgun 审查时引用已存偏好
4. 冲突时询问用户，更新 observation
```

## 存储格式（observation 摘要）

```
[taste] density=minimal | theme=dark | reject=gradient-slop | prefer=system-fonts
```

## 与 instinct-learning 边界

- **instinct-learning**：编码/工作流模式（置信度评分）
- **taste-memory**：设计/UI 偏好（主观、长期）
- 不互博：各管各的 concern

## 私密

敏感偏好用 `<private>...</private>` 阻止存储（claude-mem 边缘剥离）
