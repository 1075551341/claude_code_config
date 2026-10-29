# Catalog Agents — 按需复制

> 此目录提供领域专用 agent 定义，按需复制到项目 `.claude/agents/` 使用。
> 全局 agents 在 `~/.claude/agents/`（v12.0.0 为 16），始终可用，无需从此目录复制。
> **完整清单（41）以 [../INDEX.md](../INDEX.md) 为唯一权威**（`gen-catalog-index.py` 生成），本文不再复制列表。

## 使用策略

```
全局 agents/ (16) → 五柱核心 + gstack 审查，会话始终可用
catalog/agents/ (41) → 领域专用 + v11 降级变体，按需复制到项目
```

## v11 新入 catalog（原全局降级）

`design-shotgun` · `pair-agent` · `ios-specialist` · `land-and-deploy` · `performance-engineer`
（cso/release-engineer/product-manager/design-engineer 未入 catalog，已并入全局 agent 或 skill，见 `agents-INDEX.md` v11 变更表）

## 同名项消歧

v12 删除了与顶层同名的审查者变体（`ceo-reviewer`、`designer`、`eng-reviewer`、`qa`、`security-reviewer`）及 `security`、`context-rot-monitor`。
审查契约（七维/结论/禁改文件）由 `config/workflow.yaml` 的 `review` 段渲染进全局审查者，catalog 不再复制。新增 catalog agent 不得与顶层同名。

## 复制命令

```powershell
# 复制单个 agent 到当前项目
copy ~/.claude/catalog/agents/<name>.md .\.claude\agents\

# 或使用迁移脚本
python ~/.claude/scripts/migrate-from-legacy.py --project . --agent <name>
```

## 与全局 agents/ 的关系

- **去重原则**: catalog 中的 agent 若与全局 agents/ 同名 → 优先使用全局版本
- **特殊化原则**: catalog 提供语言/领域特定版本（如 `go-reviewer`, `rust-reviewer`）
- **按需加载**: 全局 16 agents 已覆盖通用场景，catalog 仅在特定领域需求时启用
