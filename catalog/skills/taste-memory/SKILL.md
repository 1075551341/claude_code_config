---
name: taste-memory
description: 品味记忆学习（UI 偏好跨会话）。触发词：taste memory | 品味记忆 | UI偏好 | 设计偏好学习
triggers: [品味, 设计偏好, 风格记忆, taste, minimal, dark mode]
layer: supplement
source: garrytan/gstack
disable-model-invocation: true
loading_tier: L3
---

# 跨会话品味记忆

若宿主具备记忆工具则按需写入，否则记录于项目设计文档（如 `DESIGN.md`）；敏感偏好不写入记忆。

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
1. 用户表达偏好 → 写入宿主可用记忆（标签: taste-preference）或项目设计文档
2. 新 UI 任务前 → 用可用记忆工具检索 "taste-preference" 或查阅项目设计文档
3. UI/UX 审查或 design-shotgun 探索时引用已存偏好
4. 冲突时询问用户，更新已存偏好记录
```

## 存储格式（摘要）

```
[taste] density=minimal | theme=dark | reject=gradient-slop | prefer=system-fonts
```

## 职责边界

- **通用编码/工作流交接**：记录仓库约束、技术决策与任务状态（由标准工作流/交接记录承载）
- **taste-memory**：专注设计/UI 偏好（主观、跨会话风格偏好），与通用编码/工作流交接分开记录

## 私密

敏感偏好（含账号、密钥或隐私信息）严禁写入跨会话记忆或外部存储。
