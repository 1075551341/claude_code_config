# anthropics/claude-code-action v1.0.146

> 层: 工具/集成 | 置信度: 高 | 刷新: 2026-06-24 | 来源: GitHub Releases + WebSearch 双源


## v10.5.1 delta (2026-07-17)
- **最新元数据**：8,374★；Release **v1**；`pushed_at` 2026-07-17。
- **本地映射**：CI reference。
- **来源**：GitHub API（Tier-2）。
## 核心价值

- GitHub Actions CI PR review 模板
- Claude Code 自动化审查流水线
- PR 触发 Agent 审查

## 证据

- [GitHub anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- v1.0.146（2026-06 最新）

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| CI 模板 | `templates/github-actions/` |

## 吸收决策

**模板引用** — 项目 CI 按需复制；非全局运行时。

## 互博检查

- vs gstack eng-reviewer：CI 层 vs 本地 Agent 层

## v10.1 增量

- 模板路径维持；无默认启用

## v10.3 增量

- Delta 刷新：版本追踪到 v1.0.146
- 决策不变：模板引用，项目 CI 按需复制

## v10.5 delta (2026-07-17)

- Stars：8,374；最新 Release：v1（2025-08-26，`gh api`）。
- 可吸收点：统一 `prompt` 与 `claude_args` 的 v1 配置可作为新 CI 模板的基线；既有模板引用策略不变。
- 决策不变：项目 CI 按需复制，非全局运行时。
