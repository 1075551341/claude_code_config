---
description: 多编辑器配置同步指南 v21.0（Claude Code 零同步 + AGENTS.md 适配落点）
---

# Claude 配置多编辑器同步指南

> **版本**: v21.0 (schema v2) | **日期**: 2026-11-02 | **入口**: `scripts/sync.ps1` | **引擎**: `scripts/sync-editors.ps1` | **常量单源**: `config/sync-manifest.json`
>
> **v21「AGENTS.md 适配」模型**：Claude Code 原生读 `~/.claude/CLAUDE.md`，零同步；编辑器侧把 CLAUDE.md 适配为 **AGENTS.md**，并投放真实拷贝的 rules / skills / agents。不再投放 `SPEC.md` / `MANIFEST.yaml` / 三个 `*-INDEX.md`；不再创建软链或 junction；每个通道用 `.claude-managed` 台账做孤儿清理。

## 边界原则

| 范围 | 路径 | 说明 |
| --- | --- | --- |
| **Claude Code 主环境（不同步出去）** | `~/.claude/settings.json`、`.mcp.json`、`hooks/`、`scripts/`、`commands/`、`plugins/` | 仅 CLI / Claude Code 使用 |
| **同步源（只读）** | `~/.claude/CLAUDE.md` + `rules/` + `skills/` + `agents/` | 引擎读取、适配并复制 |
| **同步目标** | `~/.cursor/`、`~/.qoder/`、`~/.trae/`、`~/.trae-cn/`、`~/.config/opencode/`、`~/.dsh/` | 实体副本；OpenCode/DSH 仅 principles 常驻块由 `principles.py` 注入，其余自管 |

`sync.ps1` 不修改 `~/.claude/settings.json`、`.mcp.json`、`hooks/`，也不触碰编辑器自有文件（Cursor `skills-cursor`、Trae `builtin_skills`、Qoder marketplace 插件/设置/MCP/memories）。

## 工程原则（R21-R25，并入铁律）

`rules/CORE.md` 的 `<!-- engineering-rules:start/end -->` 是唯一源；`scripts/principles.py sync` 将 R21-R25 段注入 `CLAUDE.md`、OpenCode/DSH `AGENTS.md` 与 `CORE.md`。`sync.ps1` 在生成编辑器入口前先执行 sync；Cursor/Qoder/Trae/Trae-CN 从 `CLAUDE.md` / `rules/CORE.md` 生成，自动携带该段。

- 校验：`python scripts/principles.py check`（R21-R25 / 5 组 / 18 子条 / 9 冲突 / 14 目标逐字一致 / 17 KiB）；14 目标 = 7 个 harness ×（入口 + CORE），optional 缺失仅 WARN。
- `validate_config.py` V22 调用该检查；staging 由 `~/.config/opencode/scripts/validate_claude_sync.py` 复核 AGENTS.md 与 CORE.md 的 R21-R25 段（CRLF 归一化，source 缺失报错）。
- 不新增 `rules/PRINCIPLES.md`；R21-R25 是 `## 铁律` 的工程决策组，不再使用独立 P 编号。

## 目标布局

| 工具 | 入口（AGENTS.md） | 规则 | skills / agents | 说明 |
| --- | --- | --- | --- | --- |
| Cursor | `~/.cursor/plugins/local/claude-config/rules/00-AGENTS.mdc` | `*.mdc`（`alwaysApply`）+ `CURSOR-EDITOR.mdc` | `~/.cursor/skills` / `~/.cursor/agents` | Cursor 无全局 AGENTS.md 加载点，规则经 local plugin |
| Qoder | `~/.qoder/rules/AGENTS.md` | `*.md`（`trigger`：`always_on` / `model_decision`） | `~/.qoder/skills` / `~/.qoder/agents` | Qoder 用户级规则目录为 `~/.qoder/rules` |
| Trae | `~/.trae/user_rules/AGENTS.md` | `*.md`（保留源 `trigger`） | `~/.trae/skills` | 全局规则目录 `~/.trae/user_rules` |
| Trae CN | `~/.trae-cn/user_rules/AGENTS.md` | `*.md`（保留源 `trigger`） | `~/.trae-cn/skills` | 全局规则目录 `~/.trae-cn/user_rules` |
| OpenCode / OpenChamber | `~/.config/opencode/AGENTS.md` | `rules/*.md`（自管） | `~/.config/opencode/skills` | 仅 principles 常驻块由 `principles.py` 注入 |
| DSH | `~/.dsh/AGENTS.md` | `rules/*.md`（自管） | `~/.dsh/skills` | 仅 principles 常驻块由 `principles.py` 注入 |

- `rules/AGENTS.md`（Agent 协作规则）在目标改名 **`AGENTS-COLLAB.md`**，避免与入口 `AGENTS.md` 重名。
- `claude-mem-maintenance` 不投放；其余 25 个 skill 全量投放。

## 常量单源：`config/sync-manifest.json`

| 消费方 | 读取内容 | 失败行为 |
| --- | --- | --- |
| `scripts/sync-editors.ps1` | `entry_source` / `entry_name` / `rules` / `skills` / `agents` / `editors` | 退出 1（manifest 必需） |
| `scripts/check.ps1` | `editors` + `rules` / `skills` / `agents` + `legacy_root_files` | 回退内置默认 |
| `templates/cursor-guard/hooks/_lib/impact_sync.py` | `root_files`（空则回退 `CLAUDE.md`）+ `editors`（规则漂移检测） | 回退内置默认 |

editors 段字段：`display`、`home`（缺席自动跳过）、`enabled`、`entry`、`rules_dir`、`rules_ext`、`rules_flavor`（`cursor` / `qoder` / `trae`）、`skills_dir`、`agents_dir`、`plugin_dir`（Cursor）、`guard_rule`、`subagent`（写入 AGENTS.md profile）。

## 模式

| 内容 | 默认 | `-Skills` | `-All` |
| --- | :--: | :-------: | :----: |
| AGENTS.md 入口（由 CLAUDE.md 适配） | ✅ | ✅ | ✅ |
| 规则实体（入口 + 6 条） | ✅ | ✅ | ✅ |
| `skills/`（25 个真实拷贝） | ❌ | ✅ | ✅ |
| `agents/`（9 个；Cursor / Qoder） | ❌ | ❌ | ✅ |
| 根文档 / 软链 / junction | ❌ | ❌ | ❌ |

- **`-Scope rules`**（默认）：入口 + 规则
- **`-Scope indexes`**：仅入口（Guard 在 CLAUDE.md 变更时调用；不会删除规则）
- **`-Scope all` / `-All`**：入口 + 规则 + skills + agents
- **`-DryRun`**：仅预览
- **`-Force`**：向后兼容参数；引擎始终按 hash 判断，稳定状态无写入（无防抖/快速路径）
- **`-CleanLegacy`**：迁移专用——删除 v1 根文件软链、旧 Cursor plugin、Trae 旧规则、skills/agents junction，然后重建
- **`-ProjectRules` / `-ProjectRulesPath`**：向项目 `.cursor/rules` 投放 `00-AGENTS.mdc` + 规则
- **`-Lint` / `-InitProject`**：仅向当前项目目录部署模板

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1                 # 入口 + 规则
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -Skills
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -All
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -All -DryRun
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -All -CleanLegacy  # 一次性迁移
```

## 内容适配

**AGENTS.md**（由 `CLAUDE.md` 生成）：
- 标题与 description 改为 `<工具> 全局配置`
- 把 `claude-mem`、`Task`、`Bash`、`Claude Code` 等专有依赖映射为本工具能力（记忆无插件则跳过并注明；工具名按同名能力执行）
- 源相对路径（`config/`、`rules/`、`skills/`、`scripts/` 等）改写为绝对 `~/.claude/...`
- 注入 profile：skills / rules 路径、记忆能力、子 Agent 名称、压缩命令、工具名映射

**规则**：
- Cursor：`description` + `alwaysApply`（`CORE`/入口 `true`，其余 `false`）
- Qoder：`trigger` + `description`（`always_on` / `model_decision`）
- Trae / Trae CN：保留源 frontmatter
- 规则正文同步做 `CLAUDE.md → AGENTS.md` 与 SSOT 路径改写；项目路径（`openspec/`、`specs/`、`archive/`、`.planning/`、`_sandbox/`）保持不变

**Skills**：
- 复制时对 `.md` 做同样的文本适配（`claude-mem` → 记忆插件、`Claude Code` → 本工具）；**不做 SSOT 路径绝对化**，技能自身的 `scripts/`、`references/`、`assets/`、`CHANGELOG.md` 等相对路径原样保留；`.py` / `.json` 等原样复制
- 适配后在内存中计算目标 hash，与目标树比较；稳定后第二次运行 0 变更

## 部署机制

1. **真实拷贝**：不创建软链/junction
2. **台账**：每个规则/skills/agents 通道写 `.claude-managed`；规则通道另写 `.claude-hashes`（源 hash + 目标 hash）。孤儿清理只删台账内条目，用户自有文件不动；`check.ps1`/`impact_sync.py` 用 hash 判定漂移（源变或目标被改都会报 stale）
3. **Cursor plugin 完全托管**：plugin rules 目录内非期望 `.mdc` 删除（旧 `00-CLAUDE.mdc`、注入变体）
4. **反向去重**：删除 `~/.cursor/rules` 中与 plugin 同名的规则，避免双份 Always-Apply
5. **同 basename 变体**：删除受管 basename 的异扩展文件（`CORE.md` vs `CORE.mdc`）
6. **幂等**：`-All` 连续运行第二次 `Changed: 0`

7. **Cursor Guard**：1.2.17（规则 + hooks 由 `deploy-cursor-guard.ps1` 部署）

## 验证

```powershell
# 只改常驻原则/规则：plain sync 即可（会自动调用 principles.py sync）
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -DryRun        # 预览
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1                # 部署
# 需要同时更新 skills/agents 时才加 -All
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -All           # + skills/ + agents/
pwsh -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1     # 去重/适配/用户规则存活
pwsh -ExecutionPolicy Bypass -File scripts/check.ps1 -Quick        # S3b 编辑器布局
python scripts/validate_config.py                                  # 深度校验
```

`check.ps1`：
- **S3**：Cursor 根/链接/守卫
- **S3b**：各工具入口、规则正文、skills/agents 数量、台账、根文件残留
- **S4b**：Cursor Guard 模板与 `00-AGENTS.mdc` / `CURSOR-EDITOR.mdc`

## 触发规则

| 改动 | 必跑 |
| --- | --- |
| `CLAUDE.md`（仅入口） | `sync.ps1 -Scope indexes` |
| `rules/*.md` | `sync.ps1`（入口 + 规则） |
| `skills/` / `agents/` | `sync.ps1 -All` |
| `templates/cursor-guard/**` | `deploy-cursor-guard.ps1` + 重启 Cursor |
| TRAE/Qoder 图谱 hook | `deploy-editor-graph-hooks.ps1` |

> Cursor Guard hooks（`~/.cursor/hooks.json`）在 prompt / 编辑 / stop 时自动运行 `sync.ps1 -Scope ... -Force`；因为 `-Force` 仍按 hash 判断，稳定状态下无写入。

## 迁移记录（v21.0）

- 删除 v1 遗留：根 `CLAUDE.md`/`SPEC.md`/`MANIFEST.yaml`/3 INDEX 软链；Cursor `00-CLAUDE.mdc` 与 6 条已删规则；Trae/Trae CN 12 个旧受管规则；`skills`/`agents` junction
- 删除前的完整备份：`~/.claude/backups/editor-migration-<时间戳>/`（含 Cursor plugin、Trae user_rules、根文件副本、junction 目标记录）
- **Qoder**：迁移前实测 `~/.qoder/{rules,skills,agents,AGENTS.md}` 均不存在，无 Claude 派生配置可删，也无需备份；本次仅新建适配产物
- 回滚：将备份目录下 `cursor/plugin/claude-config`、`trae*/user_rules` 复制回对应 home，并按 `links.json` 重建链接

## 版本史

- **v21.0 (2026-10-29)**：AGENTS.md 适配 + 真实拷贝 + schema v2（Cursor/Qoder/Trae/Trae CN）；Cursor Guard 1.2.17
- v20.21：Guard 1.2.16 安全加固（历史）
- v20.0 (v11.1.0)：多编辑器 1+N 恢复（历史）
- v19.0 (v11.0.0)：双端重构、常量单源（历史）
