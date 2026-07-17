# eyaltoledano/claude-task-master v0.43.1

> 层: 工具/集成 | 置信度: 高 | 刷新: 2026-06-19 | 来源: GitHub CHANGELOG + npm 双源


## v10.5.1 delta (2026-07-17)
- **最新元数据**：27,863★；Release **task-master-ai@0.43.1**；`pushed_at` 2026-04-28。
- **本地映射**：L4 optional；与 writing-plans **互斥**。
- **来源**：GitHub API（Tier-2）。
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

## v10.2.1 增量（双源刷新 2026-06-19）

- 稳定版 **0.43.1**（1.0.0-rc 跟踪）；保持 L4 按需
- **deferred MCP loading**（`ENABLE_EXPERIMENTAL_MCP_CLI=true`）省 ~16% 上下文（~33k tokens）→ 若启用建议开此模式

## v10.5 delta (2026-07-17)

- Stars：27,863；最新 Release：task-master-ai@0.43.1（2026-03-31，`gh api`）。
- 保持现有 L4 可选与 deferred loading 建议；该发行版仅清理历史 shell alias，无强制集成。
