---
description: 跨编辑器配置同步指南 v17.0
---

# Claude 配置跨编辑器同步指南

> **版本**: v17.0 | **日期**: 2026-06-24 | **脚本**: `scripts/sync.ps1` | **三模式**: 默认(L0入口) / `-Skills`(+skills/) / `-All`(全量) | 预览: `-DryRun`
>
> **v17 重要变更**：扩展至 7 编辑器（+qoder-cn, +trae-cn）；-cn 变体独立配置目录。同步方式不变：符号链接优先，`Copy-Item` 兜底；写入前删同名目标（去重）。

## 边界原则（Claude Code ↔ 编辑器）

| 范围 | 路径 | 说明 |
|------|------|------|
| **Claude Code 主环境（不同步出去）** | `~/.claude/settings.json`、`.mcp.json`、`hooks/`、`scripts/`、`commands/`、`plugins/` | 仅 CLI / Claude Code 使用 |
| **同步源（只读）** | `~/.claude/` 下总纲 + `skills/` `agents/` `rules/` 源文件 | `sync.ps1` 读取并链接/复制到编辑器 |
| **同步目标（仅编辑器）** | `~/.cursor/`、`%APPDATA%\devin\`、`~/.trae/`、`~/.qoder/` 等 | 软链接、联接、原生副本、路由部署均写在此 |

**`sync.ps1` 不修改** `~/.claude/settings.json`、`.mcp.json`、`hooks/`。
**`fix.ps1 -Fix`** 单独处理 Hook launcher 与编辑器 `settings.json` 中的 `env.CLAUDE_IN_EDITOR`（与内容同步无关）。

---

## v14.5 核心变更：仅L0入口 + 个人级单落点

| 变更 | v14.4 | v14.5 |
|------|-------|-------|
| **同步内容** | 全量12个rules | 仅L0关键入口（ROUTER/CLAUDE/CORE/CURSOR-EDITOR） |
| **Cursor落点** | 双落点（个人+项目） | 仅个人级 `~/.cursor/rules/` |
| **CodeArts落点** | 双落点（个人+项目） | 仅个人级 `~/.codeartsdoer/rule/` |
| **Windsurf** | 独立编辑器 | 已移除（已改名Devin） |
| **详细rules** | 全量部署到编辑器 | 通过L0路由按需Read加载 |

---

## 三模式概览（v17.0）

| 内容 | 默认（L0入口） | `-Skills` | `-All` |
|------|:--------------:|:---------:|:------:|
| L0 入口（CLAUDE.md / CORE / CLAUDE-ROUTER） | ✅ | ✅ | ✅ |
| `skills/` | ❌ | ✅ | ✅ |
| `agents/` | ❌ | ❌ | ✅ |
| `rules/`（全量） + CLAUDE.md | L0 only | L0 only | ✅ |

- **目标编辑器**：cursor / devin(`%APPDATA%\devin`) / qoder / qoder-cn / trae / trae-cn / codearts
- **rules 扩展名**：cursor·qoder·qoder-cn·codearts → `.mdc`；devin·trae·trae-cn → `.md`
- **devin 根文件名**：`AGENTS.md`（Devin CLI 全局 rules 标准）；其余编辑器 → `CLAUDE.md`
- **`-DryRun`**：仅预览，不写盘
- **永不同步**：`hooks/`、`commands/`、`scripts/`、`plugins/`、`.mcp.json`、`settings.json`

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
```
> v16：不再写 `sync-mode.json`；模式由命令行开关（`-Skills`/`-All`）即时决定。

> **v14.5+**：不再部署到项目级目录（`~/.claude/.cursor/rules/`），避免双份显示。详细rules通过L0路由按需Read加载。

**Devin**：

```
%APPDATA%\devin\AGENTS.md            全局 rules（Devin CLI 标准，L0入口）
%APPDATA%\devin\rules\*.md           L0 rule 文件（CORE/ROUTER，trigger格式）
~/.codeium/windsurf/memories/global_rules.md   Windsurf 全局 always-on（跨工作区）
```

> Devin CLI 可自动导入 `~/.claude/CLAUDE.md` 和 `.claude/skills/`，无需额外同步 skills。

**CodeArts 码道**：

```
~/.codeartsdoer/rule/*.mdc    个人级（仅L0入口：ROUTER/CLAUDE/CORE）
```

> 项目级 `~/.claude/.codeartsdoer/rule/` 已取消部署，避免双份显示。

**总纲执行链：**

```
CLAUDE-ROUTER(必加载) → CLAUDE.md → MANIFEST.yaml → *-INDEX.md → SPEC.md
→ 按需 Read skills/<name>/SKILL.md | agents/<name>.md | rules/<name>.md
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1            # 默认：仅 L0 入口
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -DryRun    # 预览
```

---

## 模式 B / C：`-Skills` 与 `-All`

| 模式 | 同步内容 | 命令 |
|------|----------|------|
| `-Skills` | L0 入口 + `skills/` | `sync.ps1 -Skills` |
| `-All` | rules（全量）+ skills + agents + CLAUDE.md | `sync.ps1 -All` |

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Skills
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -All
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -All -DryRun
```

---

## 验证

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1 -Quick
```

`check.ps1` 验证同步目标存在；S4 确认 hooks 仅在 `~/.claude`；**S4b** 检查 Cursor Guard 部署。

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

**显式同步**：聊天输入 `/sync`、`同步配置`、`刷新规则` → 执行 `sync.ps1 -All`（写入前先删同名变体再部署）。

**自动同步**：编辑 `~/.claude` 下 `rules/`、总纲、INDEX 等可同步路径后，调用 `sync.ps1`（默认 L0）或 `sync.ps1 -All`（含 rules/skills/agents）。

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

## Rules 来源与 token（v10.0）

| 来源 | 平台 | 控制方式 |
|------|------|----------|
| CLAUDE / CORE / ROUTER | 双平台 sync | 源文件去重 |
| plugin-* rules | 仅 Cursor | 禁插件即消失 |
| User Rules | 仅 Cursor Settings | 指针 + L3 skills |
| lazy rules (GIT/FRONTEND/OPENSPEC) | L0 路由按需 Read | glob 触发 |

## v10.0 加载策略

| 等级 | 同步内容 | Cursor 机制 |
|------|----------|-------------|
| L0 | CLAUDE-ROUTER + CLAUDE + CORE + CURSOR-EDITOR | alwaysApply |
| L1 | using-superpowers, change-impact-analysis | 会话常驻 |
| L2/L3 | 其余 skills | disable-model-invocation + 阶段 Read |
| L4 | agents, MCP, plugins | 显式调用 |

- **插件/MCP**：[CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)
- **运行时**：[RUNTIME_PLAYBOOK.md](RUNTIME_PLAYBOOK.md)
- **v10 任务**：[tasks-v10.md](../spec/claude-config-integration/tasks-v10.md)
- **历史详图**：`spec/claude-config-integration/plan-v9.1-token-loading.md`

---

## 去重策略（v14.5+）

每次 `sync.ps1` 写入前：

1. **L0 rules**：`Remove-AllRuleVariantsByBaseName` 删除同 basename 的 `.md`/`.mdc`/大小写变体
2. **单文件链接**：`Remove-ScopedSameTypeTarget` 先删后 `mklink`
3. **Cursor 项目 rules**：**不部署** `~/.claude/.cursor/rules/`（仅个人级 `~/.cursor/rules/`，防双份）

回归：`powershell -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1`

---

## 从 v14 升级

- **v17.0**：扩展至 7 编辑器（+qoder-cn, +trae-cn）；-cn 变体独立配置目录；devin 目标改为 `%APPDATA%\devin`（Devin CLI 标准用户配置路径），根文件名改为 `AGENTS.md`；RULES_EXT 补全 qoder-cn/trae-cn
- **v16.0**：模式参数化（`-Skills`/`-All`/`-DryRun`），弃用 `sync-mode.json`/`-Full`/`-Force`/`-Scope`；符号链接优先 + Copy-Item 兜底；devin 目标移至 `~/.claude/.devin`（v17 已纠正），rules 扩展名按编辑器区分（.mdc / .md）
- v14.5：仅L0入口同步，取消项目级双落点，移除Windsurf（已改名Devin）
- v14 索引：`skills/`、`agents/` 联接；`rules/` 改为编辑器侧单文件链接（不再联接整个目录）
- v14 总纲 7 文件：新增 `CLAUDE-ROUTER.mdc`
- v14 全量：`agents/` 联接 + `rules/`/`skills-native/` 格式转换
