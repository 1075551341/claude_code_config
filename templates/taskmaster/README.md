# Task Master 轻量模板（optional）

> 来源：eyaltoledano/claude-task-master | **不全局 skill** — 任务分解由 `skill/writing-plans` + `skill/executing-plans` 覆盖。

## 何时用

- 需要 PRD 格式 backlog，但不用 Task Master MCP 外部依赖
- 产品需求已从 `/office-hours` 或 brainstorming 产出

## 与 writing-plans 边界

| 场景 | Owner |
|------|-------|
| 非简单任务计划 | skill/writing-plans → spec/tasks 或 openspec |
| PRD 结构化输入 | 本模板 example_prd.md |
| 执行与验收 | skill/executing-plans + verification-before-completion |

## 使用

1. Copy `example_prd.md` → 项目 `.taskmaster/prd.md` 或 `docs/prd.md`
2. `/plan` 引用 PRD → writing-plans 分解
3. 可选：gh MCP 创建 issues（见 catalog handoff / writing-plans）

## MANIFEST

`concern: task_management` → owner: skill/writing-plans，模板路径：本目录。
