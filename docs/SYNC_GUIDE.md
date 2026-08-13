---
description: 多编辑器配置同步指南 v20.0（Claude Code 零同步 + 1+N 编辑器落点）
---

# Claude 配置多编辑器同步指南

> **版本**: v20.0 (v11.1.0) | **日期**: 2026-08-13 | **脚本**: `scripts/sync.ps1` | **常量单源**: `config/sync-manifest.json`
>
> **v11.1「1+N」模型**：**Claude Code 原生读 `~/.claude`，零同步**；编辑器侧 = **Cursor + qoder-cn + trae-cn + workbuddy**（清单单源 `sync-manifest.json` editors 段，home 缺席自动跳过；qoder/trae/codearts 定义保留待装）。`sync.sh`（Linux/macOS）维持已删（git 可回溯）。
>
> **推荐**：日常默认模式（根文件 + 各编辑器规则）；`-Skills` / `-All` 按需。lazy rules 经 `CLAUDE.md → Read rules/<name>.md` 按需加载，不复制。

## 边界原则（Claude Code ↔ 编辑器）

| 范围                                 | 路径                                                                                  | 说明                               |
| ------------------------------------ | ------------------------------------------------------------------------------------- | ---------------------------------- |
| **Claude Code 主环境（不同步出去）** | `~/.claude/settings.json`、`.mcp.json`、`hooks/`、`scripts/`、`commands/`、`plugins/` | 仅 CLI / Claude Code 使用          |
| **同步源（只读）**                   | `~/.claude/` 下总纲 + `skills/` `agents/` `rules/` 源文件                             | `sync.ps1` 读取并链接/复制到编辑器 |
| **同步目标（1+N）**                  | `~/.cursor/`、`~/.qoder-cn/`、`~/.trae-cn/`、`~/.workbuddy/`                          | 软链接、联接、实体副本均写在各自 home |

**`sync.ps1` 不修改** `~/.claude/settings.json`、`.mcp.json`、`hooks/`，也不触碰编辑器自有文件（如 workbuddy 的 SOUL/USER/IDENTITY/BOOTSTRAP）。
**`fix.ps1 -Fix`** 单独处理 Hook launcher 与各编辑器 `settings.json` 中的 `env.CLAUDE_IN_EDITOR`（与内容同步无关）。

---

## 常量单源：`config/sync-manifest.json`

根文件集合、插件规则特殊映射与**编辑器清单（editors 段）**只在此文件定义，三个消费方统一读取：

| 消费方                                              | 读取内容                                      | 失败回退              |
| --------------------------------------------------- | --------------------------------------------- | --------------------- |
| `scripts/sync.ps1`                                  | `root_files` + `plugin_rule_sources` + `editors` | 内置默认（须与 manifest 一致） |
| `scripts/check.ps1`                                 | `root_files` + `editors`                      | 内置默认（须与 manifest 一致） |
| `templates/cursor-guard/hooks/_lib/impact_sync.py`  | `root_files` + `editors`（规则漂移检测）      | 内置默认（须与 manifest 一致） |

> 改根文件集合或编辑器目标只改 `sync-manifest.json`；`MANIFEST.yaml` 的 `sync_targets` 仅为声明镜像。Guard 部署副本经 `deploy-cursor-guard.ps1` 刷新。editors 段字段：`home`（缺席自动跳过）、`enabled`（false=显式停用并反向扫残留）、`rules_channel` / `rules_ext`（plugin=Cursor 专用；目录名=实体复制）、`root_index`、`special`。

---

## 三模式概览（v20.0）

| 内容                                                        | 默认 | `-Skills` | `-All` |
| ----------------------------------------------------------- | :--: | :-------: | :----: |
| 6 个总纲/索引根文件（软链到 cursor/qoder-cn/trae-cn）       |  ✅  |    ✅     |   ✅   |
| Cursor local plugin 规则（实体 .mdc，每次刷新）             |  ✅  |    ✅     |   ✅   |
| qoder-cn `rules/*.mdc` + trae-cn `user_rules/*.md`（实体）  |  ✅  |    ✅     |   ✅   |
| workbuddy `CLAUDE.md` + `skills/` 联接（特例，跳根索引）    |  ✅  |    ✅     |   ✅   |
| `skills/`（Junction → cursor）                              |  ❌  |    ✅     |   ✅   |
| `agents/`（Junction → cursor）                              |  ❌  |    ❌     |   ✅   |

- **根文件（6 项，v11）**：`CLAUDE.md` + `SPEC.md` + `MANIFEST.yaml` + 三个 `*-INDEX.md`（ROUTER 并入 CLAUDE.md、agent.yaml 并入 MANIFEST harness 节）
- **`-DryRun`**：仅预览，不写盘；**`-Force`**：跳过 hash 比对强制刷新
- **`-ProjectRules`**：另将 rules 复制到**当前目录** `.cursor/rules`（显式 opt-in；CWD 为 `~/.claude` 时跳过）
- **`-Lint` / `-InitProject`**：仅向当前项目目录部署模板，不同步编辑器
- **永不同步**：`hooks/`、`commands/`、`scripts/`、`plugins/`、`.mcp.json`、`settings.json`、`~/.claude/.cursor/`（OpenSpec 本地资产）

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1            # 默认：根文件 + 插件规则
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Skills
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -All
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -All -DryRun
```

---

## 编辑器落点矩阵（v11.1）

| 编辑器    | home              | 根索引 6 项 | 规则通道                        | 特殊                                            |
| --------- | ----------------- | :---------: | ------------------------------- | ----------------------------------------------- |
| cursor    | `~/.cursor`       |     ✅      | local plugin `*.mdc`（唯一生效）| skills/agents 联接（-Skills/-All）              |
| qoder-cn  | `~/.qoder-cn`     |     ✅      | `rules/*.mdc`（实体+台账）      | —                                               |
| trae-cn   | `~/.trae-cn`      |     ✅      | `user_rules/*.md`（实体+台账）  | R19 守卫另经 TRAE AppData hook（独立于同步链）  |
| workbuddy | `~/.workbuddy`    |     ❌      | 无                              | 仅 `CLAUDE.md` + `skills/` 联接；SOUL/USER 禁触 |
| qoder     | `~/.qoder`        |     ✅      | `rules/*.mdc`                   | 未安装，缺席自动跳过                            |
| trae      | `~/.trae`         |     ✅      | `user_rules/*.md`               | 未安装，缺席自动跳过                            |
| codearts  | `~/.codeartsdoer` |     ✅      | `rule/*.mdc`                    | 未安装，缺席自动跳过                            |

> 实体复制通道带 `.claude-managed` 台账：孤儿清除只删台账内条目，编辑器目录中**用户自有规则不受影响**。

## Cursor 落点布局

> **Cursor 规则通道 = local plugin（永久方案）**：`~/.cursor/rules` 实测不生效（UI 不枚举、Agent 不加载），不做其他通道尝试；全局规则仅经 `~/.cursor/plugins/local/claude-config/rules/` 实体 .mdc 由 Cursor 加载（`sync.ps1` 每次从 SSOT 重生成 + 去重 + 孤儿清除；v11 起无 `templates/` 镜像层）。

```
~/.cursor/  （个人级）
├── CLAUDE.md, SPEC.md, MANIFEST.yaml                  (软链接)
├── skills-INDEX.md, agents-INDEX.md, rules-INDEX.md   (软链接)
├── skills/  → ~/.claude/skills/        (目录联接，-Skills/-All)
├── agents/  → ~/.claude/agents/        (目录联接，-All)
├── rules/   （保持空 — plugin 永久通道，不写实体；同名项会被清理）
└── plugins/local/claude-config/        (实体 .mdc 副本，规则唯一通道)
    ├── .cursor-plugin/plugin.json      (sync.ps1 生成，version 取自 MANIFEST)
    ├── .sync-stamp
    └── rules/
        ├── 00-CLAUDE.mdc               (= CLAUDE.md，v11 并入 ROUTER)
        ├── CORE.mdc … (rules/*.md 全量转换，README 除外)
        └── CURSOR-EDITOR.mdc           (源: templates/cursor-guard/rules/)
```

> **Cursor Settings 显示说明**
>
> | 视图                     | 读取路径                                            | 说明                                                        |
> | ------------------------ | ---------------------------------------------------- | ----------------------------------------------------------- |
> | Settings → Project Rules | `<当前工作区>/.cursor/rules/*.mdc`                  | 打开业务项目时，只有这里有文件才会显示                      |
> | Agent 全局 alwaysApply   | `~/.cursor/plugins/local/claude-config/rules/*.mdc` | **唯一通道**：plugin 实体副本；`~/.cursor/rules` 实测不生效 |
>
> **正确做法**：全局规则只维护 plugin（sync.ps1 自动刷新）；`~/.cursor/rules` 保持空。需要某项目 Settings 可见时，在该项目根执行 `sync.ps1 -ProjectRules`。改规则后跑 `sync.ps1`，若插件列表有变需**完全退出并重开 Cursor**（仅 Reload 有时不重扫 local plugins）。

**总纲执行链：**

```
CLAUDE.md(必加载，含路由) → MANIFEST.yaml → *-INDEX.md → SPEC.md
→ 按需 Read skills/<name>/SKILL.md | agents/<name>.md | rules/<name>.md
```

---

## 真源→适配→链接映射表

> 真源唯一：`~/.claude/`。不在 Cursor 目录直接改内容；格式适配由 sync.ps1 统一完成。

| 真源文件                                         | Cursor 落点                                                     | 机制                              | 原因                                            |
| ------------------------------------------------ | ---------------------------------------------------------------- | --------------------------------- | ----------------------------------------------- |
| `CLAUDE.md`                                      | `~/.cursor/CLAUDE.md`                                            | symlink                           | 纯文本，编辑器可读链接                          |
| `CLAUDE.md`（v11 并入 ROUTER）                   | `~/.cursor/plugins/local/claude-config/rules/00-CLAUDE.mdc`      | **copy**（实体 .mdc）             | plugin 唯一通道（`~/.cursor/rules` 实测不生效） |
| `rules/*.md`（除 README）                        | `~/.cursor/plugins/local/claude-config/rules/<名>.mdc`           | **copy**（改名 .mdc）             | 同上                                            |
| `templates/cursor-guard/rules/CURSOR-EDITOR.mdc` | `~/.cursor/plugins/local/claude-config/rules/CURSOR-EDITOR.mdc`  | **copy**                          | Cursor 专有规则，仅 plugin                      |
| `MANIFEST.yaml` / `SPEC.md` / `*-INDEX.md`       | `~/.cursor/` 同名                                                | symlink                           | 路由引用用                                      |
| `skills/`                                        | `~/.cursor/skills/`                                              | junction（`mklink /J`，免管理员） | 目录级                                          |
| `agents/`                                        | `~/.cursor/agents/`                                              | junction                          | 目录级                                          |
| 根文件 6 项                                      | `~/.qoder-cn/`、`~/.trae-cn/` 同名                               | symlink                           | v11.1 多编辑器根索引                            |
| `rules/*.md`（除 README）                        | `~/.qoder-cn/rules/<名>.mdc`                                     | **copy**（改名 .mdc）+ 台账       | Qoder 规则通道                                  |
| `rules/*.md`（除 README）                        | `~/.trae-cn/user_rules/<名>.md`                                  | **copy** + 台账                   | TRAE 规则通道                                   |
| `CLAUDE.md` + `skills/`                          | `~/.workbuddy/CLAUDE.md` + `~/.workbuddy/skills/`                | symlink + junction                | workbuddy 特例（无规则通道，跳根索引）          |

> 写前去重：同 basename 全变体删除后重建（`Remove-SameBasenameVariants`）；SSOT 已删的规则从 plugin/编辑器台账孤儿清除。

---

## 去重策略

每次 `sync.ps1` 写入前：

1. **同类型同名**：`Remove-SameBasenameVariants` 删除目标目录内同 basename 的全部变体（任意扩展名 / 大小写，如 `CORE.md` + `core.mdc`）
2. **精确路径**：再删除目标路径（文件或目录联接）后写入；文件优先 symlink，失败则 `Copy-Item`
3. **插件孤儿清除**：plugin rules 目录内不在投放集合的 `.mdc` 一并删除
4. **`~/.cursor/rules` 防遮蔽**：与 plugin 同 basename 的项清理（防双份 Always-Apply）
5. **编辑器通道台账清除**（v11.1）：qoder-cn/trae-cn 等实体通道按 `.claude-managed` 台账做孤儿清除——只删自己管理过的条目，**用户自有规则不动**

回归：`powershell -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1`（含 qoder-cn/trae-cn 去重 + 用户自有规则存活断言）

---

## 验证

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1 -Quick
```

`check.ps1` S3（v11.1 白名单校验）：Cursor 侧根文件/Junction/插件规则 + qoder-cn/trae-cn 根链与规则通道 hash + workbuddy CLAUDE.md/skills——managed 编辑器**缺失落点才告警**（跑 sync.ps1 修复）；`enabled=false` 的编辑器反向扫残留链。S4 确认 hooks 仅在 `~/.claude`；**S4b** 检查 Cursor Guard 部署。

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

**显式同步**：聊天输入 `/sync`、`同步配置`、`刷新规则` → 执行 `sync.ps1 -All`。
**自动同步**：Guard `impact_sync` 检测 `~/.claude` 下可同步路径（root_files / rules / skills / agents）变更后触发对应模式。
**上下文**：70% `agent_message` 提醒；90% `stop` 注入 `followup_message` 强制摘要 + 建议开新对话。

**与 Claude Code 对照**：

| 能力         | Claude Code                    | Cursor Guard                            |
| ------------ | ------------------------------ | --------------------------------------- |
| Hook 注册    | `~/.claude/settings.json`      | `~/.cursor/hooks.json`                  |
| 编辑器内执行 | 跳过（launcher）               | 全量执行                                |
| 压缩命令     | `/compact`                     | Cursor 原生 compact + `preCompact` 快照 |
| 计数文件     | `tool-call-counter.json`       | `.cursor/.state/tool-counter.json`      |
| codegraph    | MCP 自动同步（v1.5 原生监听）  | 同左（双端零 hook，v11 退役 sync hook） |

完整编辑器独有配置见 [`CURSOR_EDITOR_SETUP.md`](CURSOR_EDITOR_SETUP.md)。

---

## Rules 来源与加载策略

| 来源                               | 平台               | 控制方式         |
| ---------------------------------- | ------------------ | ---------------- |
| CLAUDE（含路由）/ CORE             | 双端 sync          | 源文件去重       |
| plugin-\* rules                    | 仅 Cursor          | 禁插件即消失     |
| User Rules                         | 仅 Cursor Settings | 指针 + L3 skills |
| lazy rules (GIT/FRONTEND/OPENSPEC) | L0 路由按需 Read   | glob 触发        |

| 等级  | 内容                                          | Cursor 机制                          |
| ----- | --------------------------------------------- | ------------------------------------ |
| L0    | CLAUDE（含路由）+ CORE + CURSOR-EDITOR        | alwaysApply（经 plugin）             |
| L1    | using-superpowers, change-impact-analysis 等  | 会话常驻                             |
| L2/L3 | 其余 skills                                   | disable-model-invocation + 阶段 Read |
| L4    | agents, MCP, plugins                          | 显式调用                             |

- **插件/MCP**：[CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)（Claude 侧 SSOT = `rules/MCP.md`）

---

## 版本史（同步链）

- **v20.0 (v11.1.0)**：**多编辑器恢复（1+N）** — 按用户决策在 v19 架构上恢复 qoder-cn/trae-cn/workbuddy 落点（未回滚 v18.4 旧脚本）；编辑器清单入 `sync-manifest.json` editors 段（home 缺席自动跳过）；新增 `Deploy-EditorRules`（实体复制 + `.claude-managed` 台账孤儿清除，用户自有规则免疫）；check.ps1 S3 反转为 managed 白名单校验；impact_sync 规则漂移检测覆盖多编辑器
- v19.0 (v11.0.0)：**双端重构** — 目标收敛为仅 Cursor（Claude Code 零同步）；删除 qoder/trae(-cn)/codearts/workbuddy 分支、`sync.sh`、`templates/cursor-claude-config-plugin/` 镜像层；常量单源 `config/sync-manifest.json`；插件规则直接从 SSOT 生成（含孤儿清除）；根文件 8→6（ROUTER 并入 CLAUDE.md、agent.yaml 并入 MANIFEST）
- v18.4：根文件 8 项部署到除 workbuddy 外所有编辑器；四处集合统一
- v18.3：移除 devin；v17.0：+qoder-cn/trae-cn；v16.0：模式参数化 + symlink 优先
- v14.5：仅 L0 入口同步、个人级单落点；v14：skills/agents 联接

> **新增编辑器**：在 `config/sync-manifest.json` editors 段加一条定义（home/rules_channel/rules_ext/root_index）即可，`sync.ps1`/`check.ps1`/`impact_sync.py` 三方自动生效；`sync.sh`（Linux/macOS）维持已删，需要时从 git 历史（tag `v10.17.0` 前后）恢复。
