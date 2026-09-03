---
description: Cursor 编辑器全局独有配置指南（与 Claude Code 低耦合）
---

# Cursor 编辑器独有配置

> Guard 模板：`templates/cursor-guard/` | 部署：`scripts/deploy-cursor-guard.ps1`

## 与 Claude Code 边界

| 项           | Claude Code                                                                   | Cursor                                                                                                           |
| ------------ | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Hooks        | `~/.claude/settings.json`（编辑器内 launcher 跳过）                           | `~/.cursor/hooks.json`                                                                                           |
| MCP 权威源   | `~/.claude/.mcp.json`                                                         | Cursor Settings 手工启用                                                                                         |
| 状态/计数    | `tool-call-counter.json`                                                      | `~/.cursor/.state/`                                                                                              |
| 规则总纲     | sync → `~/.cursor/plugins/local/claude-config/rules/*.mdc`（plugin 唯一通道） | Settings Project Rules 需 `<工作区>/.cursor/rules`：`sync.ps1 -ProjectRules`；+ `CURSOR-EDITOR.mdc`（plugin 内） |
| 配置同步桥接 | —                                                                             | 仅 `sync.ps1` 在编辑可同步资产时                                                                                 |

## 部署

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1
```

完全退出并重启 Cursor → Settings → Hooks 查看执行记录。

配置：`~/.cursor/guard-config.json`（阈值、开关）。更新模板后重跑 deploy；`-Force` 覆盖 guard-config。

**v1.2.12**：R19 禁自动新建/切换分支（`forbid_auto_branch` + `branch_requires_ask`）；R15 包管理器混用警告（pnpm 仓 `npm install`、uv/poetry 仓裸 `pip`/`python -m pip`）。复合命令（`&&` / `;` / `&` / `GIT_DIR=` / `env -i` / `{ }`）与包装（`bash -c` / `pwsh -Command` 含脚本块）同样拦截；`git checkout .` / `git checkout HEAD file` 视为路径还原。
**v1.2.11**：`verify_tracker` 对带 `resume` 的审查 Task 不计入 `reviews`（每轮须全新开审）。
**v1.2.10**：完成门不再 `followup_message`（会刷会话面板）。Stop 只刷图谱 / 全绿 sync；双审改规则驱动。`enforce_mode=off`。
**v1.2.9**：有改动即双审；独立审查 PASS/符合预期即停；仅结论不一致才再开一轮（最多 3 轮）。计划未批准零注入（CallDynamicTool/CreatePlan）；sessionEnd 刷双图 timeout 45s。
**v1.2.8**：非简单双审=修改→验证→审查循环最多 3 轮；禁止只连审不改；同轮连派不耗轮次；PASS 须已有 reviews。
**v1.2.7**：计划未批准 / CreatePlan / 零编辑 / 无 session id → Stop **不** `followup_message`；完成门不用裸词「完成」；短 R20；非简单审查最多 3 次。
**v1.2.6**：SessionStart / Stop 把双图同步 **成功或失败** 写到会话界面（`user_message`）；90% 仍不用 `followup_message`。
**v1.2.5**：90% 不再 `followup_message`（避免假用户续轮）；最多一次 `additional_context`；Stop 载荷已含该提示则跳过。
**v1.2.4**：90% Stop `followup_message` 与工具侧过载提醒**每会话只一次**；`/summarize` /「压缩上下文」重置 Guard 估算，避免压缩后仍按旧计数反复续轮。

**v1.2.3**：`hook_io.read_stdin` 解析 Cursor 3.18 stdin（UTF-8 BOM / pretty-print / Content-Length）；失败默认不写 stderr，避免 Hooks 面板刷红。本仓 `.cursor/hooks.json` 为空 stub，消除 `Failed to parse project hooks configuration`（Cursor 把缺失项目 hooks 当 ERROR）。部署后**不必重启**即可对后续 Hook 生效；项目 stub 在 Cursor 下次 reload hooks 后生效。

**v1.2.1**：完成验证 Stop `followup_message`（不能 permission deny）；每文件首次编辑后五维验收；`enforce_mode=followup`（已部署 `soft` 映射为 followup）。

**v1.1.5**：语义分离 — 「压缩上下文」= `/summarize`（压缩，Guard 不拦截）；「提取上下文」= 结构化摘要 → `session-digest.md`。

**v1.1.4**：双步压缩（已废弃，见 v1.1.5）。

**v1.1.3**：200K 窗口；`preCompact` 真实 %；handoff；`sessionEnd`。

**v1.1.2 修复**：hook 绝对路径；stdout 仅 JSON；`readline` stdin；无 BOM guard-config。

验证（一键回归，推荐）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/test-cursor-guard-regression.ps1
```

部署后回归：`... -Deploy`。报告：`scripts/test-guard-result.json`。

底层：`python scripts/test-cursor-guard-hooks.py --output scripts/test-guard-result.json`（行为断言 + JSON 合法性，需全部通过）。

## MCP 推荐（P0：codegraph）

1. 安装：`npx @colbymchenry/codegraph` → `codegraph init -i`
2. Cursor Settings → MCP 启用 codegraph
3. 索引自动保鲜：codegraph v1.5 MCP server 原生监听文件变更自动同步（300ms 静默窗 + 连接时追赶）；v11 起 Guard 不再挂 kg sync hook，也无需手动 `codegraph sync`

参考：[`templates/cursor-guard/mcp-recommended.json`](../templates/cursor-guard/mcp-recommended.json)

其余按需：gh、Context7、Exa、Playwright — 见 [`TOOL_MATCHING_GUIDE.md`](TOOL_MATCHING_GUIDE.md)。

## Skill / Agent 显式加载

| 资产     | 加载方式                          | 说明                                           |
| -------- | --------------------------------- | ---------------------------------------------- |
| L1 skill | 会话自动 + 修改时 Read            | using-superpowers、change-impact-analysis      |
| L2 skill | **Read** `skills/<name>/SKILL.md` | 进入阶段门控；`disable-model-invocation: true` |
| L3 skill | Read 或 slash/关键词 → Read       | deep-research、git-workflow 等                 |
| Agent    | Task `subagent_type`              | 见 agents-INDEX.md；fresh context（R12）       |
| Rule     | glob 匹配或 Read                  | lazy rules；FRONTEND 仅前端 glob               |

slash 命令是**路由信号**，不替代 Read 全文。

## 显式功能对照表

| 功能                 | 自动/显式                         | 实现                                                                                                           |
| -------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 配置同步 rules/总纲  | 自动 + 关键词                     | `sync_on_edit` + `sync_on_prompt` → `sync.ps1`                                                                 |
| 文档/INDEX 维护提醒  | 自动                              | `maintenance_hints`                                                                                            |
| 上下文 70% 提醒      | 自动                              | 工具估算 **与** `preCompact` 实测取较大值                                                                      |
| 上下文 90% 强制摘要  | 自动（不续轮）                    | `context_stop` → 一次 `additional_context`（不用 followup）                                                    |
| 显式「压缩上下文」   | 关键词                            | 与 **`/summarize`** 等效；Guard 不拦截                                                                         |
| 显式「提取上下文」   | 关键词                            | 结构化摘要 → `session-digest.md`（不压缩）                                                                     |
| Cursor 原生压缩      | **`/summarize`** 或「压缩上下文」 | 降低上下文环；触发 `preCompact` hook                                                                           |
| Compact 前快照       | `/summarize` 或自动满窗时         | `pre_compact_snapshot` + `cursor-context.json`                                                                 |
| 新会话交接           | 新 conversation_id                | `sessionEnd`/`stop` 写 handoff → `sessionStart` 注入                                                           |
| codegraph 优先       | soft_block（默认）                | `explore_router` + `graph_freshness`；无索引 **deny**（禁止 Grep 兜底）                                        |
| Shell 危险命令       | 自动拦截                          | `shell_guard`                                                                                                  |
| 密钥粘贴             | 自动警告                          | `prompt_secret_scan`                                                                                           |
| 会话状态一览         | 自动                              | `session_bootstrap`（ensure 双图；用户 hook cwd 是 `~/.cursor` 时用 `workspace_roots` / `.workspace-trusted`） |
| 初次修改五维验收     | 自动（每文件一次）                | `first_edit_verify`：该文件 + blast-radius 全部相关项                                                          |
| 完成验证 Stop         | 不 followup；规则驱动双审     | `verification_stop` 仅图谱 refresh / 全绿 sync（计划未批准仍 refresh） |
| R20 合格标记         | afterAgentResponse                | `r20_capture` 写入 `r20_replay_ok`                                                                             |
| 业务仓文档 companion | 自动                              | `maintenance_hints`（不限 ~/.claude）                                                                          |

### 显式同步关键词

`/sync`、`同步配置`、`sync config`、`刷新规则`、`更新索引`、`更新文档`、`同步文档`

### 压缩与上下文仪表（重要）

**Cursor 没有 `/compact`**（那是 Claude Code）。IDE 内置命令是 **`/summarize`**；CLI 是 **`/compress`**。Command Palette 里**没有**单独的 Compact/Summarize 菜单项。

#### 压缩 vs 提取（v1.1.5）

```
压缩上下文 或 /summarize  →  Cursor 原生压缩，降低上下文环
提取上下文               →  Agent 结构化摘要 → session-digest.md（不压缩）
先提取再压缩             →  提取上下文 → /summarize
```

#### 对照表

| 你想做的事                                              | 正确操作                                     |
| ------------------------------------------------------- | -------------------------------------------- |
| 降低上下文环（70% 择机 / 90% 强制，SSOT→rules/CORE.md） | **`/summarize`** 或 **「压缩上下文」**       |
| 获取结构化摘要（不压缩）                                | **「提取上下文」**                           |
| 保留决策/路径再压缩                                     | 「提取上下文」→ 等摘要 → **`/summarize`**    |
| 新会话带上轮状态                                        | handoff 或 `@session-digest.md` → 新开 Agent |
| 查看占用明细                                            | 点击输入框旁**上下文环**                     |

- 自动压缩：接近窗口上限时 Cursor 自动 summarize（`preCompact` 的 `trigger: auto`）。
- 制品路径：`~/.cursor/.state/session-digest.md`、`session-handoff.json`、`pre-compact-state.json`。

## 环境变量（可选）

| 变量                                  | 作用                            |
| ------------------------------------- | ------------------------------- |
| `CURSOR_GUARD_AUTO_SYNC=0`            | 关闭自动 sync                   |
| `CURSOR_GUARD_WARN_PCT` / `FORCE_PCT` | 压缩阈值                        |
| `CURSOR_GUARD_CODEGRAPH_FIRST=0`      | 关闭 codegraph 路由提示         |
| `CURSOR_GUARD_SHELL=0`                | 关闭 Shell 守卫                 |
| `CLAUDE_HOME`                         | sync 源目录（默认 `~/.claude`） |

## 配置一致性清单（Claude ↔ Cursor）

> **Cursor 规则通道 = local plugin（永久方案）**：`~/.cursor/rules` 实测不生效（UI 不枚举、Agent 不加载），不再尝试其他通道；规则仅经 `~/.cursor/plugins/local/claude-config/rules/` 实体 .mdc 由 Cursor 加载。

| 资产                | Claude 权威源   | Cursor 目标（plugin 通道）                                         | 同步方式                               |
| ------------------- | --------------- | ------------------------------------------------------------------ | -------------------------------------- |
| 铁律 R17 / CORE     | `rules/CORE.md` | `~/.cursor/plugins/local/claude-config/rules/CORE.mdc`             | `sync.ps1`（实体副本）                 |
| 路由 CLAUDE         | `CLAUDE.md`     | `~/.cursor/plugins/local/claude-config/rules/00-CLAUDE.mdc`（v11） | `sync.ps1`（实体副本）                 |
| 编辑器专有规则      | Guard 模板      | `~/.cursor/plugins/local/claude-config/rules/CURSOR-EDITOR.mdc`    | `deploy-cursor-guard.ps1` + `sync.ps1` |
| MCP 文档            | `rules/MCP.md`  | plugin 规则集内（`sync.ps1` 全量复制 rules/\*.md → .mdc）          | `sync.ps1`                             |
| codegraph MCP 服务  | `.mcp.json`     | `~/.cursor/mcp.json`                                               | **手工对照**（仅启用项）               |
| codegraph 路由 hook | Guard 模板      | `~/.cursor/hooks/explore_router.py`                                | `deploy-cursor-guard.ps1`              |

**推荐顺序**：先 `sync.ps1`（默认 L0 即刷新 plugin），再 `deploy-cursor-guard.ps1`。Guard 自动同步契约：`sync.ps1 -Scope rules|indexes|all [-Force]`（v18.2 支持）。

### Settings > Rules 面板预期

| 来源                                 | Settings 列表 |    Agent 加载    | 说明                                                                  |
| ------------------------------------ | :-----------: | :--------------: | --------------------------------------------------------------------- |
| User Rules 文本                      |      是       |        是        | Settings 顶部纯文本                                                   |
| 插件 rules（含 local/claude-config） |    **是**     |      **是**      | **全局 .mdc 唯一通道**（`~/.cursor/rules` 实测不生效）；sync 默认维护 |
| 个人桥接 `~/.cursor/rules/*.mdc`     | 否（UI 限制） | 否（实测不生效） | **不部署**（plugin 永久通道，空目录为正确状态）                       |
| 项目 `<workspace>/.cursor/rules/`    |      是       |        是        | **仅** `-ProjectRules` opt-in；默认不写业务项目                       |

默认：`sync.ps1` 维护 `~/.cursor/plugins/local/claude-config`（实体 .mdc 副本，规则唯一通道）；`~/.cursor/rules` 保持空。验证：Reload Window → Settings → Rules → User 应出现 claude-config 规则。

**codegraph 优先三层**（两侧一致，v10.5）：

1. 规则：`CORE` R17 + `CURSOR-EDITOR.mdc`（Cursor alwaysApply，plugin 通道）
2. Hook：`explore_router` — `enforce_mode: soft_block`（Grep/Glob 无先 codegraph 则 deny；无 `.codegraph` 降级 nudge）
3. MCP：`codegraph` 在 Cursor Settings 启用（**codebase-memory 已禁用**：全盘索引爆 CPU/内存）；项目已 `codegraph init`

## 勿做

- 勿设 `CLAUDE_HOOK_FORCE_CLI=1`（拖慢 Cursor）
- 勿软链 `~/.claude/hooks` → `~/.cursor/hooks`
- 勿复制 `~/.claude/.mcp.json` 全量到 Cursor
