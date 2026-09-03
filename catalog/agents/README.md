# Catalog Agents — 按需复制

> 此目录提供领域专用 agent 定义，按需复制到项目 `.claude/agents/` 使用。
> 全局 agents 在 `~/.claude/agents/`（v11.4.14 为 17），始终可用，无需从此目录复制。
> **完整清单（48）以 [../INDEX.md](../INDEX.md) 为唯一权威**（`gen-catalog-index.py` 生成），本文不再复制列表。

## 使用策略

```
全局 agents/ (17) → 五柱核心 + gstack 审查，会话始终可用
catalog/agents/ (48) → 领域专用 + v11 降级变体，按需复制到项目
```

## v11 新入 catalog（原全局降级）

`design-shotgun` · `pair-agent` · `ios-specialist` · `land-and-deploy` · `performance-engineer`
（cso/release-engineer/product-manager/design-engineer 未入 catalog，已并入全局 agent 或 skill，见 `agents-INDEX.md` v11 变更表）

## 同名项消歧

`ceo-reviewer`、`designer`、`eng-reviewer`、`qa`、`security-reviewer` 在顶层
`~/.claude/agents/` 也存在。**顶层为权威实现**（`agents-INDEX.md` 与 MANIFEST 均指向它），
本目录同名项是变体副本，仅在复制到项目时使用，不要在全局会话中委派。

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
- **按需加载**: 全局 17 agents 已覆盖通用场景，catalog 仅在特定领域需求时启用
