# Claude 配置多编辑器同步指南

> **版本**: v12.0.1 | **脚本**: `scripts/sync.ps1` | **常量单源**: `config/sync-manifest.json`

**1+N**：Claude Code 原生读 `~/.claude`（零同步）。编辑器仅 **cursor / qoder-cn / trae-cn / trae**。Codex / OpenCode 自管，**不生成 `AGENTS.md`**。

## 生成器

`sync.ps1` 按 `frontmatter_map` 调用 `scripts/sync_frontmatter.py` 重写前言（Cursor `.mdc` 保留 alwaysApply/globs；Claude Code 源文件已带 `paths`）。去重与 `.claude-managed` 台账仍生效。trae 补齐 `user_rules/` 部署。

```powershell
pwsh -File scripts/sync.ps1
pwsh -File scripts/sync.ps1 -All -DryRun
pwsh -File scripts/test-sync-dedup.ps1
```

改根文件集合或编辑器目标只改 `sync-manifest.json`。
