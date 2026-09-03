---
description: 多编辑器配置同步指南 v20.0（Claude Code 零同步 + 1+N 编辑器落点）
---

# Claude 配置多编辑器同步指南

> **版本**: v20.25 (v11.4.20) | **日期**: 2026-09-03 | **脚本**: `scripts/sync.ps1` | **常量单源**: `config/sync-manifest.json`
>
> **v11.1「1+N」模型**：**Claude Code 原生读 `~/.claude`，零同步**；编辑器侧 = **Cursor + qoder-cn + trae-cn + workbuddy**（v11.4.4：opencode `enabled=false`，AGENTS.md 自管，禁止 CLAUDE.md 覆盖；清单单源 `sync-manifest.json` editors 段，home 缺席自动跳过；qoder/trae/codearts 定义保留待装）。`sync.sh`（Linux/macOS）维持已删（git 可回溯）。
>
> **推荐**：日常默认模式（根文件 + 各编辑器规则）；`-Skills` / `-All` 按需。lazy rules 经 `CLAUDE.md → Read rules/<name>.md` 按需加载，不复制。

## 边界原则（Claude Code ↔ 编辑器）

| 范围                                 | 路径                                                                                  | 说明                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------- | ------------------------------------- |
| **Claude Code 主环境（不同步出去）** | `~/.claude/settings.json`、`.mcp.json`、`hooks/`、`scripts/`、`commands/`、`plugins/` | 仅 CLI / Claude Code 使用             |
| **同步源（只读）**                   | `~/.claude/` 下总纲 + `skills/` `agents/` `rules/` 源文件                             | `sync.ps1` 读取并链接/复制到编辑器    |
| **同步目标（1+N）**                  | `~/.cursor/`、`~/.qoder-cn/`、`~/.trae-cn/`、`~/.workbuddy/`                          | 软链接、联接、实体副本均写在各自 home；opencode 自管不投放 |

**`sync.ps1` 不修改** `~/.claude/settings.json`、`.mcp.json`、`hooks/`，也不触碰编辑器自有文件（如 workbuddy 的 SOUL/USER/IDENTITY/BOOTSTRAP）。
**`fix.ps1 -Fix`** 单独处理 Hook launcher 与各编辑器 `settings.json` 中的 `env.CLAUDE_IN_EDITOR`（与内容同步无关）。

---

## DSH / OpenCode 适配层（v11.4.20；手工对齐，不覆盖 AGENTS.md）

> v20.1 起即登记 DSH 消费方。OpenCode `editors.opencode.enabled=false`（v11.4.4）保持：**禁止** `CLAUDE.md` → `AGENTS.md`。

| 项 | DeepSeek Harness (`~/.dsh`) | OpenCode (`~/.config/opencode`) |
| --- | --- | --- |
| 总纲 | 自管 `AGENTS.md`（手工对齐版本映射） | 自管 `AGENTS.md` |
| 便携 CLI | `tools/graph_freshness_cli.py` | `scripts/graph_freshness_cli.py` |
| R20 机械门 | `tools/r20_check.py` | `scripts/r20_check.py` |
| 图谱插件 | 无 hook；agent CLI ensure/refresh | `plugins/graph-freshness.ts` + `verify-gate.ts` |
| 投放 | `sync.ps1`（home 存在则复制便携件）+ `deploy-editor-graph-hooks.ps1` | 同左 |
| 版本映射 | DSH 2.12 ↔ Claude 11.4.20 | OpenCode 1.12 ↔ Claude 11.4.20 |
| 禁止 | 把 Cursor `followup_message` / Claude Stop exit 2 原样搬过去；spawn `hooks/_lib/gate_cli.py` | 同左；禁止 CLAUDE.md 覆盖 AGENTS.md |

`config/sync-manifest.json` 的 **`harnesses` 段** 是清单 SSOT。`sync.ps1` 复制便携文件（不写 AGENTS.md；`graph-freshness.json` 仅在缺失时复制）。`check.ps1`：home 缺席跳过；home 存在则断言便携文件在，且 `AGENTS.md` 不是指向 `CLAUDE.md` 的软链。

场景/工具加载仍以 Claude 仓 `config/scenario-router.yaml` + `harness-capabilities.yaml` 为语义 SSOT；各端 AGENTS.md 只做 P0 指针级手工对齐。

---

## 设计内耦合清单（v11.4.1 声明——以下跨编辑器资产属 SSOT/运行态，保留勿清）

| 资产 | 归属 | 理由 |
|---|---|---|
| `templates/cursor-guard/` | Cursor Guard 部署源 | `deploy-cursor-guard.ps1` 消费 |
| `docs/CURSOR_MCP_PROFILE.md`、`docs/CURSOR_EDITOR_SETUP.md` | 1+N 架构文档 | 多端差异 SSOT |
| `config/sync-manifest.json` editors + harnesses | 多端同步常量 | sync/check/fix 三脚本 + impact_sync 共同消费 |
| `plugins/marketplaces/*`（含 .windsurf 等子树）| claude-mem 插件运行态 | 插件源码自带，gitignored |
| `openspec/`（config.yaml + changes/specs 骨架）| OpenSpec CLI 全局工作区 | 删除丢 profile 配置 |
| `mcp-configs/`（debug/fsaccess）| Claude Code 按需 MCP profile | rules/MCP.md 登记 |

> 反例（已清理）：`~/.claude/.cursor/`、`.trae/` 为编辑器在 .claude cwd 的误生成残留（v11.4.1 删除）；新增跨编辑器目录时一律落各自 home，禁止写入 .claude。

---

## 常量单源：`config/sync-manifest.json`

根文件集合、插件规则特殊映射、**编辑器清单（editors 段）**与 **harnesses 段**只在此文件定义。**云端 Agent 不能写本机 `C:\Users\DELL\.claude`**（仓根即该目录）。本机落地示例：

```powershell
cd C:\Users\DELL\.claude
git fetch origin
git checkout cursor/v11-config-alignment-04a6
git pull origin cursor/v11-config-alignment-04a6
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1
pwsh -ExecutionPolicy Bypass -File scripts/deploy-editor-graph-hooks.ps1
```

已合入 `main` 则 `git checkout main` 后 `git pull`。脱敏核验：`settings.json` enabledPlugins 对照 SPEC；OpenCode `AGENTS.md` 不得为 CLAUDE.md 软链。

| 消费方                                             | 读取内容                                         | 失败回退                       |
| -------------------------------------------------- | ------------------------------------------------ | ------------------------------ |
| `scripts/sync.ps1`                                 | `root_files` + `plugin_rule_sources` + `editors` + `harnesses` | 内置默认（须与 manifest 一致） |
| `scripts/check.ps1`                                | `root_files` + `editors` + `harnesses`                         | 内置默认（须与 manifest 一致） |
| `templates/cursor-guard/hooks/_lib/impact_sync.py` | `root_files` + `editors`（规则漂移检测）         | 内置默认（须与 manifest 一致） |

> 改根文件集合或编辑器目标只改 `sync-manifest.json`；`MANIFEST.yaml` 的 `sync_targets` 仅为声明镜像。Guard 部署副本经 `deploy-cursor-guard.ps1` 刷新。editors 段字段：`home`（缺席自动跳过）、`enabled`（false=显式停用并反向扫残留）、`rules_channel` / `rules_ext`（plugin=Cursor 专用；目录名=实体复制）、`root_index`、`special`。

---

## 三模式概览（v20.0）

| 内容                                                       | 默认 | `-Skills` | `-All` |
| ---------------------------------------------------------- | :--: | :-------: | :----: |
| 6 个总纲/索引根文件（软链到 cursor/qoder-cn/trae-cn）      |  ✅  |    ✅     |   ✅   |
| Cursor local plugin 规则（实体 .mdc，每次刷新）            |  ✅  |    ✅     |   ✅   |
| qoder-cn `rules/*.mdc` + trae-cn `user_rules/*.md`（实体） |  ✅  |    ✅     |   ✅   |
| workbuddy `CLAUDE.md` + `skills/` 联接（特例，跳根索引）   |  ✅  |    ✅     |   ✅   |
| opencode `AGENTS.md`（v11.4.4 解耦，不再投放）             |  ❌  |    ❌     |   ❌   |
| `skills/`（Junction → cursor）                             |  ❌  |    ✅     |   ✅   |
| `agents/`（Junction → cursor）                             |  ❌  |    ❌     |   ✅   |

- **根文件（6 项，v11）**：`CLAUDE.md` + `SPEC.md` + `MANIFEST.yaml` + 三个 `*-INDEX.md`（ROUTER 并入 CLAUDE.md、agent.yaml 并入 MANIFEST harness 节）
- **`-DryRun`**：仅预览，不写盘；**`-Force`**：跳过 hash 比对强制刷新
- **`-ProjectRules`**：另将 rules 复制到**当前目录** `.cursor/rules`（显式 opt-in；CWD 为 `~/.claude` 时跳过）
- **`-Lint` / `-InitProject`**：仅向当前项目目录部署模板，不同步编辑器
- **永不同步**：`hooks/`、`commands/`、`scripts/`、`plugins/`、`.mcp.json`、`settings.json`（v11.4.1：原 `~/.claude/.cursor/`、`.trae/` 误生成残留已清理）

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1            # 默认：根文件 + 插件规则（PS5.1 回退用 powershell）
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -Skills
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -All
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -All -DryRun
```

---

## 编辑器落点矩阵（v11.1）

| 编辑器    | home              | 根索引 6 项 | 规则通道                         | 特殊                                            |
| --------- | ----------------- | :---------: | -------------------------------- | ----------------------------------------------- |
| cursor    | `~/.cursor`       |     ✅      | local plugin `*.mdc`（唯一生效） | skills/agents 联接（-Skills/-All）              |
| qoder-cn  | `~/.qoder-cn`     |     ✅      | `rules/*.mdc`（实体+台账）       | —                                               |
| trae-cn   | `~/.trae-cn`      |     ✅      | `user_rules/*.md`（实体+台账）   | R19 守卫另经 TRAE AppData hook（独立于同步链）  |
| workbuddy | `~/.workbuddy`    |     ❌      | 无                               | 仅 `CLAUDE.md` + `skills/` 联接；SOUL/USER 禁触 |
| qoder     | `~/.qoder`        |     ✅      | `rules/*.mdc`                    | 未安装，缺席自动跳过                            |
| trae      | `~/.trae`         |     ✅      | `user_rules/*.md`                | 未安装，缺席自动跳过                            |
| codearts  | `~/.codeartsdoer` |     ✅      | `rule/*.mdc`                     | 未安装，缺席自动跳过                            |

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
> | ------------------------ | --------------------------------------------------- | ----------------------------------------------------------- |
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
| ------------------------------------------------ | --------------------------------------------------------------- | --------------------------------- | ----------------------------------------------- |
| `CLAUDE.md`                                      | `~/.cursor/CLAUDE.md`                                           | symlink                           | 纯文本，编辑器可读链接                          |
| `CLAUDE.md`（v11 并入 ROUTER）                   | `~/.cursor/plugins/local/claude-config/rules/00-CLAUDE.mdc`     | **copy**（实体 .mdc）             | plugin 唯一通道（`~/.cursor/rules` 实测不生效） |
| `rules/*.md`（除 README）                        | `~/.cursor/plugins/local/claude-config/rules/<名>.mdc`          | **copy**（改名 .mdc）             | 同上                                            |
| `templates/cursor-guard/rules/CURSOR-EDITOR.mdc` | `~/.cursor/plugins/local/claude-config/rules/CURSOR-EDITOR.mdc` | **copy**                          | Cursor 专有规则，仅 plugin                      |
| `MANIFEST.yaml` / `SPEC.md` / `*-INDEX.md`       | `~/.cursor/` 同名                                               | symlink                           | 路由引用用                                      |
| `skills/`                                        | `~/.cursor/skills/`                                             | junction（`mklink /J`，免管理员） | 目录级                                          |
| `agents/`                                        | `~/.cursor/agents/`                                             | junction                          | 目录级                                          |
| 根文件 6 项                                      | `~/.qoder-cn/`、`~/.trae-cn/` 同名                              | symlink                           | v11.1 多编辑器根索引                            |
| `rules/*.md`（除 README）                        | `~/.qoder-cn/rules/<名>.mdc`                                    | **copy**（改名 .mdc）+ 台账       | Qoder 规则通道                                  |
| `rules/*.md`（除 README）                        | `~/.trae-cn/user_rules/<名>.md`                                 | **copy** + 台账                   | TRAE 规则通道                                   |
| `CLAUDE.md` + `skills/`                          | `~/.workbuddy/CLAUDE.md` + `~/.workbuddy/skills/`               | symlink + junction                | workbuddy 特例（无规则通道，跳根索引）          |

> 写前去重：同 basename 全变体删除后重建（`Remove-SameBasenameVariants`）；SSOT 已删的规则从 plugin/编辑器台账孤儿清除。

---

## 去重策略

每次 `sync.ps1` 写入前：

1. **同类型同名**：`Remove-SameBasenameVariants` 删除目标目录内同 basename 的全部变体（任意扩展名 / 大小写，如 `CORE.md` + `core.mdc`）
2. **精确路径**：再删除目标路径（文件或目录联接）后写入；文件优先 symlink，失败则 `Copy-Item`
3. **插件孤儿清除**：plugin rules 目录内不在投放集合的 `.mdc` 一并删除
4. **`~/.cursor/rules` 防遮蔽**：与 plugin 同 basename 的项清理（防双份 Always-Apply）
5. **编辑器通道台账清除**（v11.1）：qoder-cn/trae-cn 等实体通道按 `.claude-managed` 台账做孤儿清除——只删自己管理过的条目，**用户自有规则不动**

回归：`pwsh -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1`（含 qoder-cn/trae-cn 去重 + 用户自有规则存活断言）

---

## 验证

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/check.ps1 -Quick
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
| 配置           | `~/.cursor/guard-config.json`               | 70%/90% 阈值、同步开关、`verification.enforce_mode=off` |
| 项目 hooks stub | 本仓 `.cursor/hooks.json`（空 `hooks`）      | Cursor 3.18 把缺失项目 hooks 标成 parse ERROR；空文件即可静音 |

**部署**：

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1
```

**显式同步**：聊天输入 `/sync`、`同步配置`、`刷新规则` → 执行 `sync.ps1 -All`。
**自动同步**：Guard `impact_sync` 检测 `~/.claude` 下可同步路径（root_files / rules / skills / agents）变更后触发对应模式。
**上下文**：70% `agent_message` 提醒；90% `stop` 注入一次 `additional_context`（不用 followup_message）。

**与 Claude Code 对照**：

| 能力         | Claude Code                   | Cursor Guard                            |
| ------------ | ----------------------------- | --------------------------------------- |
| Hook 注册    | `~/.claude/settings.json`     | `~/.cursor/hooks.json`                  |
| 编辑器内执行 | 跳过（launcher）              | 全量执行                                |
| 压缩命令     | `/compact`                    | Cursor 原生 compact + `preCompact` 快照 |
| 计数文件     | `tool-call-counter.json`      | `.cursor/.state/tool-counter.json`      |
| codegraph    | MCP 自动同步（v1.5 原生监听） | 同左（双端零 hook，v11 退役 sync hook） |
| 完成验证     | Stop `exit 2` + R20 反空模板  | 规则驱动双审（无 followup）；Stop 仅图谱 refresh / 全绿 sync |
| 初次修改验收 | PostToolUse 并入 tracker      | `first_edit_verify`（每文件一次）                      |
| 文档 companion | stop-readme / 维护提醒        | `maintenance_hints`（含业务仓）                        |

Guard 1.2.3：`hook_io.read_stdin` 解析 BOM / pretty-print / Content-Length，避免 Hooks 面板被 `stdin JSON incomplete` 刷红。

完整编辑器独有配置见 [`CURSOR_EDITOR_SETUP.md`](CURSOR_EDITOR_SETUP.md)。

---

## Rules 来源与加载策略

| 来源                               | 平台               | 控制方式         |
| ---------------------------------- | ------------------ | ---------------- |
| CLAUDE（含路由）/ CORE             | 双端 sync          | 源文件去重       |
| plugin-\* rules                    | 仅 Cursor          | 禁插件即消失     |
| User Rules                         | 仅 Cursor Settings | 指针 + L3 skills |
| lazy rules (GIT/FRONTEND/OPENSPEC) | L0 路由按需 Read   | glob 触发        |

| 等级  | 内容                                         | Cursor 机制                         |
| ----- | -------------------------------------------- | ----------------------------------- |
| L0    | CLAUDE（含路由）+ CORE + CURSOR-EDITOR       | alwaysApply（经 plugin）            |
| L1    | using-superpowers, change-impact-analysis 等 | 会话常驻                            |
| L2/L3 | 其余 skills + agents/MCP/plugins             | disable-model-invocation + 显式调用 |

- **插件/MCP**：[CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)（Claude 侧 SSOT = `rules/MCP.md`）

---

## 版本史（同步链）

- **v20.25 (v11.4.20)**：场景 load 注入 + capability_resolver；本机拉取优化分支而非只 `git pull` main。version_map ↔ 11.4.20。
- **v20.24 (v11.4.19)**：L0/Stop 轮次句括号同形；version_map ↔ 11.4.19。
- **v20.23 (v11.4.18)**：现行操作句与 L0 轮次口径对齐；version_map ↔ 11.4.18。
- **v20.22 (v11.4.17)**：本机落地 Bypass + 云端不能写本机 home；DSH/OpenCode version_map ↔ 11.4.17。
- **v20.21 (v11.4.16)**：check.ps1 Expand-UserHome 与 sync/deploy 对齐；README TTHW/验证 `pwsh -ExecutionPolicy Bypass -File`。
- **v20.20 (v11.4.15)**：README 本机 `git pull`+deploy；sync Expand-UserHome；harnesses 进常量表；OpenCode enabled=false 显式 skip。
- **v20.19 (v11.4.14)**：`sync.ps1` 复制 harness 便携件（不写 AGENTS.md）；场景路由加载器；Stop/Guard 消费审前双图键。Guard 1.2.12。
- **v20.18 (v11.4.13)**：场景路由 YAML + harness 能力图；独立审前双图；inherit 并行审查（禁倍率档）；`harnesses` 段；补 DSH 适配层正文；workbuddy enabled=true（home 缺席跳过）。
- **v20.17 (v11.4.12)**：一次找齐再集中改；每轮独立审查必须全新开审（禁止 resume）。Guard 1.2.11；DSH 2.12 / OpenCode 1.12。
- **v20.16 (v11.4.11)**：审查只找问题、修改走 change-implementer；配置/文档/注释必须同步。DSH 2.10 / OpenCode 1.10。
- **v20.15 (v11.4.10)**：Cursor 完成门不再 followup（规则驱动双审）。Guard 1.2.10；DSH 2.9 / OpenCode 1.9。90% 用 `additional_context`（文档与实现对齐）。
- **v20.14 (v11.4.9)**：有改动即双审；独立审查 PASS 即停，仅结论不一致才再开一轮（最多 3 轮）。计划未批准零注入；Windows `/X:/` 路径；sessionEnd 刷双图。Guard 1.2.9；DSH 2.8 / OpenCode 1.8。
- **v20.13 (v11.4.8)**：非简单双审=修改→验证→审查循环最多 3 轮；禁止只连审不改。Guard 1.2.8；DSH 2.7 / OpenCode 1.7。
- **v20.12 (v11.4.7)**：Cursor Guard 1.2.7 — 计划未批准 / CreatePlan / 零编辑禁止 followup；短 R20；非简单双审最多 3 次。DSH 2.6 / OpenCode 1.6 手工对齐（`sync.ps1` 仍不覆盖 AGENTS.md；禁止把 followup_message 搬到 DSH/OpenCode）。
- **v20.11 (v11.4.6)**：图谱保鲜配置提取到 DSH / OpenCode（便携 CLI + 本端 json；OpenCode plugin；DSH 总纲强制）。`sync.ps1` 仍不覆盖 AGENTS.md。DSH 2.5 / OpenCode 1.5：ensure/规则注入每会话一次，idle refresh 冷却，禁止压缩提示续轮；R20 影响范围经 `r20_check.py`（DSH `tools/`、OpenCode `scripts/`）与 OpenCode `verify-gate.ts` 机械门对齐。
- **v20.10 (v11.4.6)**：图谱保鲜硬门——会话先 ensure 双图、无图 deny；`sync.ps1` 仅验证全绿后跑（不因 SessionStart / rules 过期）。TRAE/Qoder hook 注册走 `deploy-editor-graph-hooks.ps1`，不进 sync.ps1
- **v20.9 (v11.4.5)**：MCP 分工（内置>plugin>MCP；CRG=上下文/影响面/风险/审查/PR；DevTools/Postgres 中断启用）+ Stop 六维纠错续轮。DSH `AGENTS.md` 2.2 / OpenCode `AGENTS.md` 1.2 手工对齐（**不改**各端 plugin/MCP 开关）。sync.ps1 只刷新 Cursor/qoder/trae 规则通道
- **v20.8 (v11.4.4)**：opencode 出站切断 — `enabled=false`，不再投放 `CLAUDE.md → AGENTS.md`；DSH/OpenCode 各自独立总纲与验证门，禁止运行时依赖 `~/.claude`
- **v20.7 (v11.4.1)**：DSH 手工对齐补 **v1.3.4↔v11.4.1**——移植需求指纹实质比对（R20/终验模板/verification skill 小节）、审查结论机械检测、IMPACT 文本化；DSH 本地演进：启动链零更新化（更新移交计划任务「DSH Update Check」，仅本体损坏才自愈）、MCP 本地化直启（`~/.dsh/tools/mcp` 三件套 + repomap 直连 .venv，pin 对齐 .mcp.json）、桌面端窗口就绪即分级热加载第二批 MCP（dsh-deferred-mcp.ps1）、双端插件 web-ui-all 0.3.3/modlens 3.24.2/dshmarket 1.29.2（web 移除独立 sidebar 防 126）、desktop openBrowser:false
- **v20.5 (v11.3.5)**：验证准则分解评分（llm-as-a-verifier：观察输出优先/准则三问/1-20 评分/重复评估/成对比较消偏/进度止损）；DSH 映射补 v1.3.3↔v11.3.5（合并源指针顺带修复 v11.3.3/11.3.4 滞后）
- **v20.4 (v11.3.4)**：门控短指针 + 初次修改五维验收 + R20 反空模板；Cursor stop followup 等效硬门
- **v20.3 (v11.3.3)**：R20 文档/备注与文件/配置一致；加载口径统一 L0–L3（本表去掉 L4 行）
- **v20.2 (v11.3.2)**：R20 逐条回放强化（改前成熟/全局 + 漏改/原功能）；DSH 映射补 v1.2.x↔v11.3.2
- **v20.1 (v11.3.1)**：新增「DSH 适配层」小节（DSH 消费方登记 + 手工对齐协议）；编辑器口径统一 7 编辑器（qoder/trae/codearts 保留待装、home 缺席自动跳过）
- **v20.0 (v11.1.0)**：**多编辑器恢复（1+N）** — 按用户决策在 v19 架构上恢复 qoder-cn/trae-cn/workbuddy 落点（未回滚 v18.4 旧脚本）；编辑器清单入 `sync-manifest.json` editors 段（home 缺席自动跳过）；新增 `Deploy-EditorRules`（实体复制 + `.claude-managed` 台账孤儿清除，用户自有规则免疫）；check.ps1 S3 反转为 managed 白名单校验；impact_sync 规则漂移检测覆盖多编辑器
- v19.0 (v11.0.0)：**双端重构** — 目标收敛为仅 Cursor（Claude Code 零同步）；删除 qoder/trae(-cn)/codearts/workbuddy 分支、`sync.sh`、`templates/cursor-claude-config-plugin/` 镜像层；常量单源 `config/sync-manifest.json`；插件规则直接从 SSOT 生成（含孤儿清除）；根文件 8→6（ROUTER 并入 CLAUDE.md、agent.yaml 并入 MANIFEST）
- v18.4：根文件 8 项部署到除 workbuddy 外所有编辑器；四处集合统一
- v18.3：移除 devin；v17.0：+qoder-cn/trae-cn；v16.0：模式参数化 + symlink 优先
- v14.5：仅 L0 入口同步、个人级单落点；v14：skills/agents 联接

> **新增编辑器**：在 `config/sync-manifest.json` editors 段加一条定义（home/rules_channel/rules_ext/root_index）即可，`sync.ps1`/`check.ps1`/`impact_sync.py` 三方自动生效；`sync.sh`（Linux/macOS）维持已删，需要时从 git 历史（tag `v10.17.0` 前后）恢复。
