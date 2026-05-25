---
name: handoff
description: 将当前会话压缩为 handoff 文档，供新会话或子 agent 续作。触发：/clear 前、子 agent 切换、长任务断点。excludes claude-mem SSOT 与 skill/structured-artifacts 制品职责。
layer: catalog
source: mattpocock/skills
excludes: [plugin/claude-mem, skill/structured-artifacts]
---

# Handoff（catalog 按需）

> 来源：mattpocock/skills | 跨会话 SSOT 仍由 **claude-mem**；结构化制品由 **structured-artifacts**；本 skill 生成**单次任务**交接摘要。

## 何时用

- `/clear` 或新会话前保存进度
- 子 agent 接手前注入最小上下文
- 长任务逻辑断点（GSD 50% 阈值）

## Handoff 文档结构

```markdown
# Handoff — <task-id>

## 目标
## 已完成
## 当前状态（文件/测试/分支）
## 未决决策
## 下一步（≤3 条）
## 勿重复（已尝试且失败）
```

输出路径建议：`.planning/handoff-<date>.md` 或项目 `STATE.md` 增量更新。

## 与 claude-mem / structured-artifacts 边界

| 层 | Owner | 内容 |
|----|-------|------|
| 跨会话记忆 | claude-mem plugin | 观察、模式、检索 |
| 项目制品 | structured-artifacts | PROJECT/REQUIREMENTS/ROADMAP/STATE |
| 单次交接 | **本 skill** | 当前任务快照 |

## 复制到项目

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project . --skill handoff
```
