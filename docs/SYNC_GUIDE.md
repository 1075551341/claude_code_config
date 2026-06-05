---
description: 跨编辑器配置同步指南 v14
---

# Claude 配置跨编辑器同步指南

> **版本**: v14.0 | **脚本**: `scripts/sync.ps1` | **模式**: 索引（默认） / 全量（`-Full`）

## 双模式概览

| 内容 | 索引模式（默认） | 全量模式（`-Full`） |
|------|:----------------:|:-------------------:|
| CLAUDE.md / SPEC.md / MANIFEST.yaml | ✅ 软链接 | ✅ 软链接 |
| skills-INDEX / agents-INDEX / rules-INDEX | ✅ 软链接 | ✅ 软链接 |
| `skills/` | ✅ 目录联接 | ❌ 移除联接 → `skills-native/` 格式转换 |
| `agents/` | ✅ 目录联接 | ✅ 目录联接 |
| `rules/` | ✅ 目录联接 | ❌ 移除联接 → 原生 `.mdc`/`.md` 副本 |
| sync-mode.json | `index` | `full` |

**不同步（两种模式均适用）**：`hooks/`、`commands/`、`scripts/`、`plugins/`、`.mcp.json`、`settings.json`

---

## 模式 A：索引同步（默认）

```
~/.cursor/  （Windsurf/Trae/Qoder 同理）
├── CLAUDE.md, SPEC.md, MANIFEST.yaml     (软链接)
├── skills-INDEX.md, agents-INDEX.md, rules-INDEX.md  (软链接)
├── skills/  → ~/.claude/skills/        (目录联接)
├── agents/  → ~/.claude/agents/        (目录联接)
├── rules/   → ~/.claude/rules/         (目录联接)
└── sync-mode.json                        { "mode": "index" }
```

**总纲执行链：**

```
CLAUDE.md → MANIFEST.yaml(owner) → *-INDEX.md(发现) → SPEC.md(法典)
→ Read skills/<name>/SKILL.md | agents/<name>.md | rules/<name>.md
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Force   # 强制重建
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -DryRun  # 预演
```

---

## 模式 B：全量同步（`-Full`）

在索引内容基础上，额外生成编辑器原生格式副本：

| 资产 | 输出路径（Cursor 示例） |
|------|-------------------------|
| rules | `~/.cursor/rules/*.mdc` |
| skills | `~/.cursor/skills-native/<name>/SKILL.md` |
| agents | `~/.cursor/agents/` 目录联接（不转换） |

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Full -Force
```

**切回索引模式：**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Force
```

---

## 路径互斥说明

- `rules/`、`skills/` 在同一路径不能既是联接又是实体目录。
- **Index → Full**：移除 `rules/`、`skills/` 联接，写入原生副本。
- **Full → Index**：备份并删除原生 `rules/`、`skills-native/`，重建联接。
- 备份目录：`~/.claude/backups/<timestamp>/`

---

## 软链接目标

| 编辑器 | 路径 |
|--------|------|
| Cursor | `~/.cursor/` |
| Windsurf | `~/.windsurf/` |
| Trae | `~/.trae/` |
| Qoder | `~/.qoder/` |
| CodeArts Agent | `%APPDATA%/codearts-agent/User/` |

---

## 验证

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1 -Quick
python scripts/validate_config.py
```

`check.ps1` S3 段读取 `sync-mode.json` 并按 index/full 分别验证。

---

## 从 v13 升级

- v13 索引模式仅同步 6 个总纲文件
- v14 索引模式额外联接 `skills/`、`agents/`、`rules/`
- v14 全量模式：`agents/` 联接 + `rules/`/`skills-native/` 格式转换
- Linux/macOS 见 `scripts/sync.sh`（索引联接；Full 转换请用 Windows `sync.ps1 -Full`）

---

## 索引文件

`*-INDEX.md` 由 `generate-indexes.py` 生成，含名称、描述、加载级别三列。
