---
description: 跨编辑器配置同步指南 v17.0
---

# Claude 配置跨编辑器同步指南

> **版本**: v18.0 | **日期**: 2026-06-29 | **脚本**: `scripts/sync.ps1` | **推荐**: **默认 L0**（省 token）| `-Skills` / `-All` 按需
>
> **v10.4 推荐**：日常 Cursor 使用 **默认模式（L0）** — 仅 CORE + ROUTER + CURSOR-EDITOR；lazy rules 经 `CLAUDE-ROUTER → Read rules/<name>.md` 按需加载。首次离线或需全量 rules 时用 `-All`。

## 边界原则（Claude Code ↔ 编辑器）

| 范围                                 | 路径                                                                                  | 说明                                     |
| ------------------------------------ | ------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Claude Code 主环境（不同步出去）** | `~/.claude/settings.json`、`.mcp.json`、`hooks/`、`scripts/`、`commands/`、`plugins/` | 仅 CLI / Claude Code 使用                |
| **同步源（只读）**                   | `~/.claude/` 下总纲 + `skills/` `agents/` `rules/` 源文件                             | `sync.ps1` 读取并链接/复制到编辑器       |
| **同步目标（仅编辑器）**             | `~/.cursor/`、`%APPDATA%\devin\`、`~/.trae/`、`~/.qoder/` 等                          | 软链接、联接、原生副本、路由部署均写在此 |

**`sync.ps1` 不修改** `~/.claude/settings.json`、`.mcp.json`、`hooks/`。
**`fix.ps1 -Fix`** 单独处理 Hook launcher 与编辑器 `settings.json` 中的 `env.CLAUDE_IN_EDITOR`（与内容同步无关）。

---

## v14.5 核心变更：仅L0入口 + 个人级单落点

| 变更             | v14.4               | v14.5                                            |
| ---------------- | ------------------- | ------------------------------------------------ |
| **同步内容**     | 全量12个rules       | 仅L0关键入口（ROUTER/CLAUDE/CORE/CURSOR-EDITOR） |
| **Cursor落点**   | 双落点（个人+项目） | 仅个人级 `~/.cursor/rules/`                      |
| **CodeArts落点** | 双落点（个人+项目） | 仅个人级 `~/.codeartsdoer/rule/`                 |
| **Windsurf**     | 独立编辑器          | 已移除（已改名Devin）                            |
| **详细rules**    | 全量部署到编辑器    | 通过L0路由按需Read加载                           |

---

## 三模式概览（v17.0）

| 内容                                        | 默认（L0入口） | `-Skills` | `-All` |
| ------------------------------------------- | :------------: | :-------: | :----: |
| L0 入口（CLAUDE.md / CORE / CLAUDE-ROUTER） |       ✅       |    ✅     |   ✅   |
| `skills/`                                   |       ❌       |    ✅     |   ✅   |
| `agents/`                                   |       ❌       |    ❌     |   ✅   |
| `rules/`（全量） + CLAUDE.md                |    L0 only     |  L0 only  |   ✅   |

- **目标编辑器**：cursor / devin(`%APPDATA%\devin`) / qoder / qoder-cn / trae / trae-cn / codearts
- **rules 扩展名**：cursor·qoder·qoder-cn·codearts → `.mdc`；devin·trae·trae-cn → `.md`
- **devin 根文件名**：`AGENTS.md`（Devin CLI 全局 rules 标准）；其余编辑器 → `CLAUDE.md`
- **`-DryRun`**：仅预览，不写盘
- **永不同步**：`hooks/`、`commands/`、`scripts/`、`plugins/`、`.mcp.json`、`settings.json`、`~/.claude/.cursor/`（OpenSpec 本地资产）

---

## 模式 A：索引同步（默认）

```
~/.cursor/  （Cursor 个人级；Devin/Trae/Qoder 同理）
├── CLAUDE.md, CLAUDE-ROUTER.mdc, SPEC.md, MANIFEST.yaml  (软链接)
├── skills-INDEX.md, agents-INDEX.md, rules-INDEX.md      (软链接)
├── skills/  → ~/.claude/skills/        (目录联接)
├── agents/  → ~/.claude/agents/        (目录联接)
├── rules/   (实体 .mdc；Cursor Settings 对软链索引不稳定 → Copy)
│   ├── 00-CLAUDE-ROUTER.mdc
│   ├── CORE.mdc
│   └── CURSOR-EDITOR.mdc                 (sync / deploy-cursor-guard)
```

> **Cursor Settings 显示说明（v18.1）**
>
> | 视图                     | 读取路径                                                               | 说明                                                         |
> | ------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------ |
> | Settings → Project Rules | `<当前工作区>/.cursor/rules/*.mdc`                                     | 打开业务项目时，只有这里有文件才会出现在图2                  |
> | Agent 全局 alwaysApply   | `~/.cursor/rules/*.mdc`                                                | sync 默认写入这里；Agent 会加载，但不等于 Project Rules 面板 |
> | 打开 `~/.claude` 工作区  | 若同时存在 `~/.cursor/rules` **与** `~/.claude/.cursor/rules` 同名文件 | Settings 会 **双份显示**（图1）                              |
>
> **正确做法**：全局只维护 `~/.cursor/rules`；需要某项目 Settings 可见时，在该项目根执行 `pwsh -File sync.ps1 -ProjectRules`（或 `-All -ProjectRules`）。**不要**把同一套规则再镜像进 `~/.claude/.cursor/rules`。

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

| 模式      | 同步内容                                   | 命令               |
| --------- | ------------------------------------------ | ------------------ |
| `-Skills` | L0 入口 + `skills/`                        | `sync.ps1 -Skills` |
| `-All`    | rules（全量）+ skills + agents + CLAUDE.md | `sync.ps1 -All`    |

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

| 层             | 路径                                        | 职责                                 |
| -------------- | ------------------------------------------- | ------------------------------------ |
| 模板（版本化） | `~/.claude/templates/cursor-guard/`         | hooks 源码 SSOT                      |
| 运行时         | `~/.cursor/hooks.json` + `~/.cursor/hooks/` | Cursor 原生 hook                     |
| 状态           | `~/.cursor/.state/`                         | 计数/压缩快照（与 `~/.claude` 隔离） |
| 配置           | `~/.cursor/guard-config.json`               | 70%/90% 阈值、同步开关               |

**部署**：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1
```

**显式同步**：聊天输入 `/sync`、`同步配置`、`刷新规则` → 执行 `sync.ps1 -All`（写入前先删同名变体再部署）。

**自动同步**：编辑 `~/.claude` 下 `rules/`、总纲、INDEX 等可同步路径后，调用 `sync.ps1`（默认 L0）或 `sync.ps1 -All`（含 rules/skills/agents）。

**上下文**：70% `agent_message` 提醒；90% `stop` 注入 `followup_message` 强制摘要 + 建议开新对话。

**与 Claude Code 对照**：

| 能力         | Claude Code                    | Cursor Guard                            |
| ------------ | ------------------------------ | --------------------------------------- |
| Hook 注册    | `~/.claude/settings.json`      | `~/.cursor/hooks.json`                  |
| 编辑器内执行 | 跳过（launcher）               | 全量执行                                |
| 压缩命令     | `/compact`                     | Cursor 原生 compact + `preCompact` 快照 |
| 计数文件     | `tool-call-counter.json`       | `.cursor/.state/tool-counter.json`      |
| codegraph    | MCP + post-codegraph-sync(CLI) | MCP 优先路由；无 post-codegraph-sync    |

完整编辑器独有配置见 [`CURSOR_EDITOR_SETUP.md`](CURSOR_EDITOR_SETUP.md)。

---

## Rules 来源与 token（v10.0）

| 来源                               | 平台               | 控制方式         |
| ---------------------------------- | ------------------ | ---------------- |
| CLAUDE / CORE / ROUTER             | 双平台 sync        | 源文件去重       |
| plugin-\* rules                    | 仅 Cursor          | 禁插件即消失     |
| User Rules                         | 仅 Cursor Settings | 指针 + L3 skills |
| lazy rules (GIT/FRONTEND/OPENSPEC) | L0 路由按需 Read   | glob 触发        |

## v10.0 加载策略

| 等级  | 同步内容                                      | Cursor 机制                          |
| ----- | --------------------------------------------- | ------------------------------------ |
| L0    | CLAUDE-ROUTER + CLAUDE + CORE + CURSOR-EDITOR | alwaysApply                          |
| L1    | using-superpowers, change-impact-analysis     | 会话常驻                             |
| L2/L3 | 其余 skills                                   | disable-model-invocation + 阶段 Read |
| L4    | agents, MCP, plugins                          | 显式调用                             |

- **插件/MCP**：[CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)
- **运行时**：[RUNTIME_PLAYBOOK.md](RUNTIME_PLAYBOOK.md)
- **当前设计**：[design-v10.5.1.md](../spec/claude-config-integration/design-v10.5.1.md)
- **当前计划**：[2026-07-29-v10.6-optimization.md](superpowers/plans/2026-07-29-v10.6-optimization.md)

## 真源→适配→链接映射表（v10.6.0）

> 真源唯一：`~/.claude/`。不在任何编辑器目录直接改内容；格式适配由 sync.ps1 统一完成。

| 真源文件 | Cursor 落点 | 机制 | 原因 |
| ------------------------------ | -------------------------------------- | ------------ | ------------------------------ |
| `CLAUDE.md` | `~/.cursor/CLAUDE.md` | symlink | 纯文本，编辑器可读链接 |
| `CLAUDE-ROUTER.mdc` | `~/.cursor/CLAUDE-ROUTER.mdc` + `rules/00-CLAUDE-ROUTER.mdc` | symlink + **copy** | rules 目录内必须实体（Settings 不索引软链） |
| `rules/CORE.md` | `~/.cursor/rules/CORE.mdc` | **copy**（改名 .mdc） | 同上；扩展名适配 |
| `templates/cursor-guard/rules/CURSOR-EDITOR.mdc` | `~/.cursor/rules/CURSOR-EDITOR.mdc` | **copy** | Cursor 专有规则，仅部署到 Cursor |
| `MANIFEST.yaml` / `SPEC.md` / `*-INDEX.md` | `~/.cursor/` 同名 | symlink | 路由引用用 |
| `skills/` | `~/.cursor/skills/` | junction（`mklink /J`，免管理员） | 目录级 |
| `agents/` | `~/.cursor/agents/` | junction | 目录级 |
| `rules/*.md`（`-All` 时） | `~/.cursor/rules/<name>.mdc` | **copy**（改名） | 实体副本，先删同名变体再写 |
| Devin 特化 | `%APPDATA%\devin\AGENTS.md` + `rules/*.md` | copy `.md` | Devin CLI 标准 |

> 写前去重：同 basename 全变体删除后重建（`Remove-SameBasenameVariants`）；非本工具生成的用户手动文件只报告不删除（详见 sync.ps1 日志）。

---

## 去重策略（v18.0+）

每次 `sync.ps1` 写入前（`Sync-File`）：

1. **同类型同名**：`Remove-SameBasenameVariants` 删除目标目录内同 basename 的全部变体（任意扩展名 / 大小写，如 `CORE.md` + `core.mdc`）
2. **精确路径**：再 `Remove-Target` 删除目标路径（文件或目录联接）
3. **写入**：优先 symlink，失败则 `Copy-Item`
4. **Cursor 项目 rules**：**不部署** `~/.claude/.cursor/rules/`（仅个人级 `~/.cursor/rules/`，防双份）

回归：`powershell -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1`

---

## 从 v14 升级

- **v17.0**：扩展至 7 编辑器（+qoder-cn, +trae-cn）；-cn 变体独立配置目录；devin 目标改为 `%APPDATA%\devin`（Devin CLI 标准用户配置路径），根文件名改为 `AGENTS.md`；RULES_EXT 补全 qoder-cn/trae-cn
- **v16.0**：模式参数化（`-Skills`/`-All`/`-DryRun`），弃用 `sync-mode.json`/`-Full`/`-Force`/`-Scope`；符号链接优先 + Copy-Item 兜底；devin 目标移至 `~/.claude/.devin`（v17 已纠正），rules 扩展名按编辑器区分（.mdc / .md）
- v14.5：仅L0入口同步，取消项目级双落点，移除Windsurf（已改名Devin）
- v14 索引：`skills/`、`agents/` 联接；`rules/` 改为编辑器侧单文件链接（不再联接整个目录）
- v14 总纲 7 文件：新增 `CLAUDE-ROUTER.mdc`
- v14 全量：`agents/` 联接 + `rules/`/`skills-native/` 格式转换
