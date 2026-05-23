# /clear — 切换任务重置

结束当前任务上下文，开始新任务时使用。

## 何时使用

- 用户切换完全不同的话题或项目
- 上一任务已 ship/归档，无需保留上下文
- 上下文已污染，需要干净起点

## 行为

1. 丢弃当前任务中间状态（计划草稿、未提交假设）
2. 保留：用户偏好、项目 CLAUDE.md、claude-mem 跨会话记忆
3. 重新走 Tool-First：`using-superpowers` → 判断简单/非简单

## 注意

- 不等于 `/compact`（压缩保留进度摘要）
- 非简单新任务仍须 `brainstorming` HARD-GATE
