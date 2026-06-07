---
description: 跨编辑器配置同步指南 v14
---

# Claude 配置跨编辑器同步指南

> **版本**: v14.1 | **日期**: 2026-06-07 | **配置**: `sync-mode.json` | **模式**: 索引（默认） / 全量（`-Full`）

## 边界原则（Claude Code ↔ 编辑器）

| 范围 | 路径 | 说明 |
|------|------|------|
| **Claude Code 主环境（不同步出去）** | `~/.claude/settings.json`、`.mcp.json`、`hooks/`、`scripts/`、`commands/`、`plugins/` | 仅 CLI / Claude Code 使用 |
| **同步源（只读）** | `~/.claude/` 下总纲 + `skills/` `agents/` `rules/` 源文件 | `sync.ps1` 读取并链接/复制到编辑器 |
| **同步目标（仅编辑器）** | `~/.cursor/`、`~/.windsurf/` 等 | 软链接、联接、原生副本、路由部署均写在此 |

**`sync.ps1` 不修改** `~/.claude/settings.json`、`.mcp.json`、`hooks/`。  
**`fix.ps1 -Fix`** 单独处理 Hook launcher 与编辑器 `settings.json` 中的 `env.CLAUDE_IN_EDITOR`（与内容同步无关）。

---

## 双模式概览

| 内容 | 索引模式（默认） | 全量模式（`-Full`） |
|------|:----------------:|:-------------------:|
| 7 总纲（含 `CLAUDE-ROUTER.mdc`） | ✅ 软链接 | ✅ 软链接 |
| `skills/` | ✅ 目录联接 | ❌ → `skills-native/` 格式转换 |
| `agents/` | ✅ 目录联接 | ✅ 目录联接 |
| `rules/` | ✅ 编辑器实体目录：单文件软链接 + 路由副本 | ❌ → 原生 `.mdc`/`.md` 副本 |
| sync-mode.json | `index` | `full` |

**永不同步**：`hooks/`、`commands/`、`scripts/`、`plugins/`、`.mcp.json`、`settings.json`

---

## 模式 A：索引同步（默认）

```
~/.cursor/  （Windsurf/Trae/Qoder 同理）
├── CLAUDE.md, CLAUDE-ROUTER.mdc, SPEC.md, MANIFEST.yaml  (软链接)
├── skills-INDEX.md, agents-INDEX.md, rules-INDEX.md      (软链接)
├── skills/  → ~/.claude/skills/        (目录联接)
├── agents/  → ~/.claude/agents/        (目录联接)
├── rules/   (实体目录，仅编辑器侧)
│   ├── 00-CLAUDE-ROUTER.mdc              (必加载，从总纲部署)
│   ├── CLAUDE.mdc                        (总纲副本，源 ~/.claude/CLAUDE.md)
│   ├── CORE.mdc, GIT.mdc, …            (原生 .mdc 副本，源更新时强制刷新)
└── sync-mode.json                        { "mode": "index" }
```

**总纲执行链：**

```
CLAUDE-ROUTER(必加载) → CLAUDE.md → MANIFEST.yaml → *-INDEX.md → SPEC.md
→ 按需 Read skills/<name>/SKILL.md | agents/<name>.md | rules/<name>.md
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Force
```

---

## 模式 B：全量同步（`-Full`）

| 资产 | 输出路径（Cursor 示例） |
|------|-------------------------|
| rules | `~/.cursor/rules/*.mdc` + `00-CLAUDE-ROUTER.mdc` |
| skills | `~/.cursor/skills-native/<name>/SKILL.md` |
| agents | `~/.cursor/agents/` 目录联接 |

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Full -Force
```

---

## 验证

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1 -Quick
```

`check.ps1` S3 段读取 `sync-mode.json` 并按 index/full 分别验证；S4 确认 hooks 仅在 `~/.claude`。

---

## 从 v13 升级

- v14 索引：`skills/`、`agents/` 联接；`rules/` 改为编辑器侧单文件链接（不再联接整个目录）
- v14 总纲 7 文件：新增 `CLAUDE-ROUTER.mdc`
- v14 全量：`agents/` 联接 + `rules/`/`skills-native/` 格式转换
