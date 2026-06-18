# eyaltoledano/claude-task-master

> 层: 工具/集成 | 置信度: 高 | 刷新: 2026-06-16

## 核心价值

- PRD → 任务分解 MCP
- core/standard/all 三级工具集（~70% token 减少）
- 长项目任务管理
- `TASK_MASTER_TOOLS=core` 按需启用

## 证据

- [GitHub eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master)
- `docs/reference/task-master-integration.md`

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| task_master | `MANIFEST.yaml` L4 optional |
| MCP | `.mcp.json` optional 分组 |
| 互斥 | excludes `[task_master_mcp, writing-plans]` 上下文 |

## 吸收决策

**L4 可选** — Superpowers 主规划；PRD 长项目触发。

## 互博检查

- vs writing-plans：Superpowers 主；task-master 长 PRD 专用

## v10.1 增量

- 维持 L4 按需；不默认常驻 MCP
