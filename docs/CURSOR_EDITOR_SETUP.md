---
description: Cursor 编辑器全局独有配置指南（与 Claude Code 低耦合）
---

# Cursor 编辑器独有配置

> Guard 模板：`templates/cursor-guard/` | 部署：`scripts/deploy-cursor-guard.ps1`

## 与 Claude Code 边界

| 项           | Claude Code                                                       | Cursor                              |
| ------------ | ----------------------------------------------------------------- | ----------------------------------- |
| Hooks        | `~/.claude/settings.json`（编辑器内 launcher 跳过）               | `~/.cursor/hooks.json`              |
| MCP 权威源   | `~/.claude/.mcp.json`                                             | Cursor Settings 手工启用            |
| 状态/计数    | `tool-call-counter.json`                                          | `~/.cursor/.state/`                 |
| 规则总纲     | sync → `~/.cursor/rules/*.mdc` + 当前工作区 `.cursor/rules/*.mdc` | + `CURSOR-EDITOR.mdc`（Guard 部署） |
| 配置同步桥接 | —                                                                 | 仅 `sync.ps1` 在编辑可同步资产时    |

## 部署

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1
```

完全退出并重启 Cursor → Settings → Hooks 查看执行记录。

配置：`~/.cursor/guard-config.json`（阈值、开关）。更新模板后重跑 deploy；`-Force` 覆盖 guard-config。

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
3. codegraph 自带文件监听增量索引，**无需** Claude `post-codegraph-sync`

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

| 功能                | 自动/显式                         | 实现                                                       |
| ------------------- | --------------------------------- | ---------------------------------------------------------- |
| 配置同步 rules/总纲 | 自动 + 关键词                     | `sync_on_edit` + `sync_on_prompt` → `sync.ps1`             |
| 文档/INDEX 维护提醒 | 自动                              | `maintenance_hints`                                        |
| 上下文 70% 提醒     | 自动                              | 工具估算 **与** `preCompact` 实测取较大值                  |
| 上下文 90% 强制摘要 | 自动                              | `context_stop` → `followup_message`                        |
| 显式「压缩上下文」  | 关键词                            | 与 **`/summarize`** 等效；Guard 不拦截                     |
| 显式「提取上下文」  | 关键词                            | 结构化摘要 → `session-digest.md`（不压缩）                 |
| Cursor 原生压缩     | **`/summarize`** 或「压缩上下文」 | 降低上下文环；触发 `preCompact` hook                       |
| Compact 前快照      | `/summarize` 或自动满窗时         | `pre_compact_snapshot` + `cursor-context.json`             |
| 新会话交接          | 新 conversation_id                | `sessionEnd`/`stop` 写 handoff → `sessionStart` 注入       |
| codegraph 优先      | soft_block（默认）                | `explore_router` + `CURSOR-EDITOR.mdc`；无索引则降级 nudge |
| Shell 危险命令      | 自动拦截                          | `shell_guard`                                              |
| 密钥粘贴            | 自动警告                          | `prompt_secret_scan`                                       |
| 会话状态一览        | 自动                              | `session_bootstrap`                                        |

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

| 你想做的事               | 正确操作                                     |
| ------------------------ | -------------------------------------------- |
| 降低上下文环（85%→更低） | **`/summarize`** 或 **「压缩上下文」**       |
| 获取结构化摘要（不压缩） | **「提取上下文」**                           |
| 保留决策/路径再压缩      | 「提取上下文」→ 等摘要 → **`/summarize`**    |
| 新会话带上轮状态         | handoff 或 `@session-digest.md` → 新开 Agent |
| 查看占用明细             | 点击输入框旁**上下文环**                     |

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

| 资产                | Claude 权威源   | Cursor 目标                                                             | 同步方式                                                    |
| ------------------- | --------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------- |
| 铁律 R17 / CORE     | `rules/CORE.md` | `~/.cursor/rules/CORE.mdc` + `.cursor/rules/CORE.mdc`                   | `sync.ps1`                                                  |
| 路由 CLAUDE         | `CLAUDE.md`     | `~/.cursor/rules/CLAUDE.mdc` + `.cursor/rules/CLAUDE.mdc`               | `sync.ps1`                                                  |
| MCP 文档            | `rules/MCP.md`  | `~/.cursor/rules/MCP.mdc` + `.cursor/rules/MCP.mdc`                     | `sync.ps1`                                                  |
| codegraph MCP 服务  | `.mcp.json`     | `~/.cursor/mcp.json`                                                    | **手工对照**（仅 codegraph 等需启用的项）                   |
| codegraph 路由 hook | Guard 模板      | `~/.cursor/hooks/explore_router.py`                                     | `deploy-cursor-guard.ps1`                                   |
| 编辑器专有规则      | Guard 模板      | `~/.cursor/rules/CURSOR-EDITOR.mdc` + `.cursor/rules/CURSOR-EDITOR.mdc` | `deploy-cursor-guard.ps1` + `sync.ps1`（sync 已白名单保护） |

**推荐顺序**：先 `sync.ps1 -Scope all -Force`，再 `deploy-cursor-guard.ps1`。

### Settings > Rules 面板预期

| 来源                              | Settings 列表 | Agent 加载 | 说明                                                      |
| --------------------------------- | :-----------: | :--------: | --------------------------------------------------------- |
| User Rules 文本                   |      是       |     是     | Settings 顶部纯文本                                       |
| 插件 rules                        |      是       |     是     | 带插件名                                                  |
| 个人桥接 `~/.cursor/rules/*.mdc`  | 不稳定/依版本 |     是     | 兼容跨项目加载                                            |
| 项目 `<workspace>/.cursor/rules/` |      是       |     是     | sync 写入当前 `~/.claude` 工作区，Settings > Rules 可枚举 |
| `~/.claude/.cursor/`              |      是       |     是     | 当前工作区 Cursor 配置目录；sync 仅管理其 `rules/`        |

sync 同时部署个人桥接规则到 `~/.cursor/rules/`，以及当前工作区项目规则到 `~/.claude/.cursor/rules/`。验证：Settings > Rules 与 Agent 上下文环。

**codegraph 优先三层**（两侧一致，v10.5）：

1. 规则：`CORE` R17 + `CURSOR-EDITOR.mdc`（Cursor alwaysApply）
2. Hook：`explore_router` — `enforce_mode: soft_block`（Grep/Glob 无先 codegraph 则 deny；无 `.codegraph` 降级 nudge）
3. MCP：`codegraph` + `codebase-memory` 必须在 Cursor Settings 启用；项目已 `codegraph init`

## 勿做

- 勿设 `CLAUDE_HOOK_FORCE_CLI=1`（拖慢 Cursor）
- 勿软链 `~/.claude/hooks` → `~/.cursor/hooks`
- 勿复制 `~/.claude/.mcp.json` 全量到 Cursor
