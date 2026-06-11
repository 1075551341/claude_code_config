---
description: 跨编辑器配置同步指南 v14.5
---

# Claude 配置跨编辑器同步指南

> **版本**: v14.5 | **日期**: 2026-06-11 | **配置**: `sync-mode.json` | **模式**: 索引（默认） / 全量（`-Full`）

## 边界原则（Claude Code ↔ 编辑器）

| 范围 | 路径 | 说明 |
|------|------|------|
| **Claude Code 主环境（不同步出去）** | `~/.claude/settings.json`、`.mcp.json`、`hooks/`、`scripts/`、`commands/`、`plugins/` | 仅 CLI / Claude Code 使用 |
| **同步源（只读）** | `~/.claude/` 下总纲 + `skills/` `agents/` `rules/` 源文件 | `sync.ps1` 读取并链接/复制到编辑器 |
| **同步目标（仅编辑器）** | `~/.cursor/`、`~/.devin/`、`~/.trae/`、`~/.qoder/` 等 | 软链接、联接、原生副本、路由部署均写在此 |

**`sync.ps1` 不修改** `~/.claude/settings.json`、`.mcp.json`、`hooks/`。
**`fix.ps1 -Fix`** 单独处理 Hook launcher 与编辑器 `settings.json` 中的 `env.CLAUDE_IN_EDITOR`（与内容同步无关）。

---

## v14.5 核心变更：仅L0入口 + 个人级单落点

| 变更 | v14.4 | v14.5 |
|------|-------|-------|
| **同步内容** | 全量12个rules | 仅L0关键入口（ROUTER/CLAUDE/CORE/CURSOR-EDITOR） |
| **Cursor落点** | 双落点（个人+项目） | 仅个人级 `~/.cursor/rules/` |
| **CodeArts落点** | 双落点（个人+项目） | 仅个人级 `~/.config/codeartsdoer/rule/` |
| **Windsurf** | 独立编辑器 | 已移除（已改名Devin） |
| **详细rules** | 全量部署到编辑器 | 通过L0路由按需Read加载 |

---

## 双模式概览

| 内容 | 索引模式（默认） | 全量模式（`-Full`） |
|------|:----------------:|:-------------------:|
| 7 总纲（含 `CLAUDE-ROUTER.mdc`） | ✅ 软链接 | ✅ 软链接 |
| `skills/` | ✅ 目录联接 | ❌ → `skills-native/` 格式转换 |
| `agents/` | ✅ 目录联接 | ✅ 目录联接 |
| `rules/` | ✅ 仅L0入口部署 | ❌ → 仅L0入口（原生格式） |
| sync-mode.json | `index` | `full` |

**永不同步**：`hooks/`、`commands/`、`scripts/`、`plugins/`、`.mcp.json`、`settings.json`

---

## 模式 A：索引同步（默认）

```
~/.cursor/  （Cursor 个人级；Devin/Trae/Qoder 同理）
├── CLAUDE.md, CLAUDE-ROUTER.mdc, SPEC.md, MANIFEST.yaml  (软链接)
├── skills-INDEX.md, agents-INDEX.md, rules-INDEX.md      (软链接)
├── skills/  → ~/.claude/skills/        (目录联接)
├── agents/  → ~/.claude/agents/        (目录联接)
├── rules/   (实体目录，仅L0入口)
│   ├── 00-CLAUDE-ROUTER.mdc              (必加载，从总纲部署)
│   ├── CLAUDE.mdc                        (总纲副本，源 ~/.claude/CLAUDE.md)
│   ├── CORE.mdc                          (L0骨架，源 ~/.claude/rules/CORE.md)
│   └── CURSOR-EDITOR.mdc                 (Cursor专属守护层)
└── sync-mode.json                        { "mode": "index" }
```

> **v14.5+**：不再部署到项目级目录（`~/.claude/.cursor/rules/`），避免双份显示。详细rules通过L0路由按需Read加载。

**Devin**：

```
~/.claude/.devin/rules/*.md          L0入口（trigger格式）
~/.codeium/windsurf/memories/global_rules.md   全局 always-on（跨工作区）
~/.devin/                            7 总纲软链 + skills/agents 联接
```

**CodeArts 码道**：

```
~/.config/codeartsdoer/rule/*.mdc    个人级（仅L0入口：ROUTER/CLAUDE/CORE）
```

> 项目级 `~/.claude/.codeartsdoer/rule/` 已取消部署，避免双份显示。

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
| rules（仅L0） | `~/.cursor/rules/*.mdc`（ROUTER/CLAUDE/CORE/CURSOR-EDITOR） |
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

`check.ps1` S3 段读取 `sync-mode.json` 并按 index/full 分别验证；S4 确认 hooks 仅在 `~/.claude`；**S4b** 检查 Cursor Guard 部署。

---

## Cursor Guard（编辑器独立守护层）

> Claude Code 的 `settings.json` hooks 在 Cursor 内由 `_editor_hook_launcher` 跳过。Cursor 侧能力由 **Cursor Guard** 单独提供。

| 层 | 路径 | 职责 |
|----|------|------|
| 模板（版本化） | `~/.claude/templates/cursor-guard/` | hooks 源码 SSOT |
| 运行时 | `~/.cursor/hooks.json` + `~/.cursor/hooks/` | Cursor 原生 hook |
| 状态 | `~/.cursor/.state/` | 计数/压缩快照（与 `~/.claude` 隔离） |
| 配置 | `~/.cursor/guard-config.json` | 70%/90% 阈值、同步开关 |

**部署**：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1
```

**显式同步**：聊天输入 `/sync`、`同步配置`、`刷新规则` → 执行 `sync.ps1 -Scope all -Force`（L0 入口先删同名变体再部署）。

**自动同步**：编辑 `~/.claude` 下 `rules/`、总纲、INDEX 等可同步路径后，按 MANIFEST 影响图调用 `sync.ps1 -Scope rules|indexes|all`（`skills/`/`agents/` 联接不重复 sync）。

**上下文**：70% `agent_message` 提醒；90% `stop` 注入 `followup_message` 强制摘要 + 建议开新对话。

**与 Claude Code 对照**：

| 能力 | Claude Code | Cursor Guard |
|------|-------------|--------------|
| Hook 注册 | `~/.claude/settings.json` | `~/.cursor/hooks.json` |
| 编辑器内执行 | 跳过（launcher） | 全量执行 |
| 压缩命令 | `/compact` | Cursor 原生 compact + `preCompact` 快照 |
| 计数文件 | `tool-call-counter.json` | `.cursor/.state/tool-counter.json` |
| codegraph | MCP + post-codegraph-sync(CLI) | MCP 优先路由；无 post-codegraph-sync |

完整编辑器独有配置见 [`CURSOR_EDITOR_SETUP.md`](CURSOR_EDITOR_SETUP.md)。

---

## Rules 来源与 token（v9.2）

| 来源 | 平台 | 控制方式 |
|------|------|----------|
| CLAUDE / CORE / ROUTER | 双平台 sync | 源文件去重；CORE 保留 R12–R18 + 编码规范 |
| plugin-* rules | 仅 Cursor | 禁插件即消失 |
| User Rules | 仅 Cursor Settings | 4 行指针（[snippet](../templates/cursor-user-rules-snippet.txt)） |
| lazy rules (GIT/FRONTEND/OPENSPEC) | L0路由按需Read | 匹配文件前零成本 |

## v9.2 加载策略（Token 减负）

| 等级 | 同步内容 | Cursor 机制 |
|------|----------|-------------|
| L0 | CLAUDE-ROUTER + CLAUDE + CORE + CURSOR-EDITOR | alwaysApply rules（`~/.cursor/rules/` 个人级单落点） |
| L1 | using-superpowers, change-impact-analysis | 会话常驻（无 disable） |
| L2/L3 | 其余 `skills/` | `disable-model-invocation: true` + 阶段 Read |
| L4 | agents, MCP, plugins | 显式调用 |

- **插件/MCP**：见 [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)；Claude Code `.mcp.json` 常驻 5
- **运行时**：见 [RUNTIME_PLAYBOOK.md](RUNTIME_PLAYBOOK.md)
- **详图**：`spec/claude-config-integration/plan-v9.1-token-loading.md`（v9.2 补全见 MANIFEST v9.2）

---

## 从 v14 升级

- v14.5：仅L0入口同步，取消项目级双落点，移除Windsurf（已改名Devin）
- v14 索引：`skills/`、`agents/` 联接；`rules/` 改为编辑器侧单文件链接（不再联接整个目录）
- v14 总纲 7 文件：新增 `CLAUDE-ROUTER.mdc`
- v14 全量：`agents/` 联接 + `rules/`/`skills-native/` 格式转换
