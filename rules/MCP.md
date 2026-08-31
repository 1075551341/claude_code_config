---
trigger: model_decision
description: MCP 服务器配置规范。触发：修改 MCP 配置、添加/删除 MCP 服务器、验证 MCP 配置一致性。
---

# MCP 服务器配置规范

## 适用场景

- 修改 MCP 服务器配置
- 添加/删除 MCP 服务器
- 验证 MCP 配置一致性

## 核心规则

### 1. 单一权威源

`.mcp.json` 是 Claude Code MCP 服务器配置的**唯一权威源**（常驻）。

- 添加常驻服务器 → 只修改 `.mcp.json`
- 删除服务器 → 只修改 `.mcp.json`
- settings.json **禁止**定义 mcpServers（v3.0+）
- Cursor 侧权威：`~/.cursor/mcp.json` + Plugins（见 `docs/CURSOR_MCP_PROFILE.md`）

### 2. 常驻架构（内置 > plugin > MCP）

选择顺序（v11.4.5）：**编辑器/工作区内置工具 > 同名同功能 plugin > MCP > 按需中断启用**。`.mcp.json` 只放**没有官方 plugin 且内置不可用**的项；`mcp/servers.json` 是派生分组视图。

| 层         | 服务器 | 位置 |
| ---------- | ------ | ---- |
| 本地代码   | codegraph, code-review-graph, serena | `.mcp.json` |
| 远端探索   | grep | `.mcp.json` |
| Plugins    | context7、exa、playwright、firecrawl（Claude `enabledPlugins=true`）；chrome-devtools **默认 false** | 禁止再写入 `.mcp.json` |
| 不对齐 Cursor 面板 | github（plugin=false 且不写 MCP）；firecrawl 不写 MCP（Claude 走 plugin） | 见下 |
| debug      | chrome-devtools 回退配方（**禁止自动 merge**；仅用户手动启用后 Plugin 仍不可用时） | `mcp-configs/debug.json` |
| fsaccess   | fs | `mcp-configs/fsaccess.json` |
| ops        | redis, sqlite, docker, postgres（默认不加载；postgres 走 DATABASE_URL） | `mcp-configs/ops.json` |
| collab     | figma, linear, notion, slack | `mcp-configs/collab.json`（仅声明） |

> **plugin 优先**：同名 plugin + MCP 禁止双挂，删 MCP 留 plugin。Qoder/OpenCode/DSH 无对等 marketplace plugin 时用钉版本 MCP（各端自管，禁止经 sync 覆盖）。

> **已删除**：`aider-repo-map`、`sequential-thinking`（不要再加回常驻）。不装竞品 code-graph plugin（sdsrss/dorkian 等）；不启用 `ralph-loop`。

> **chrome-devtools / postgres：默认关，需要时中断**。Agent **禁止**自动 merge debug/ops 进 `.mcp.json`。需要联调或查库时停止当前步骤，请用户在 Plugin 面板手动打开 chrome-devtools，或自行设 `DATABASE_URL` 后启用 postgres；用户确认后再继续。

### 3. 按需启用 profile（debug / fsaccess / ops）

用户**手动**启用时：

1. 打开对应 `mcp-configs/<profile>.json`
2. 将 `mcpServers` 对象合并进 `~/.claude/.mcp.json` 的 `mcpServers`（仅当无对等 plugin）
3. 重启 Claude Code
4. 任务完成后移除并重启（恢复 `.mcp.json` 常驻集）

Agent 不得代执行上述 merge。chrome-devtools 优先开 Plugin；postgres 优先用户设 `DATABASE_URL` 后启用 ops 条目。

> **playwright / context7 / exa**：Claude/Cursor 走 **Plugins**。chrome-devtools 默认关。Qoder/OpenCode/DSH 无 plugin 则钉 MCP，chrome-devtools 默认 disabled。postgres 默认禁用。

Cursor 侧见 `docs/CURSOR_MCP_PROFILE.md`（不同步 `.mcp.json`）。Python 系（serena / uv / uvx）经 `scripts/python-mcp.ps1` 启动：清 PYTHONHOME/PYTHONPATH，避免残缺前缀导致 `encodings` 崩溃。编辑器 `mcp.json` 各自手工维护，**禁止经 sync.ps1 复制**。

### 4. 本地代码三工具分工（防互博）

三者能力有重叠，按下表选择；**禁止**用 serena 替代 codegraph 做 R17 日常探索；**禁止**用 codegraph 做 test-gap。

| 工具              | 定位                                         | 何时用                                                                                         | 何时不用                         |
| ----------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------- |
| codegraph         | **R17 探索主位**（怎么运作）                 | 符号/调用链/依赖/「这段代码如何工作」；无 CRG 图时的 blast-radius                              | test-gap；git-diff 风险评分      |
| serena            | 符号级精确编辑 + LSP 诊断                    | 跨文件重命名/插入/替换符号体、取 `get_diagnostics_for_file`                                    | 只读探索（应走 codegraph）       |
| code-review-graph | **精准上下文 / 变更影响 / 风险 / 审查 / PR** | `get_minimal_context`、`get_impact_radius`、`get_affected_flows`、`detect_changes`、`get_review_context`、开 PR 前风险门 | 替代 R17「怎么运作」的日常探索   |

> 有 `.code-review-graph/` 时：改前强制 CRG 上下文+影响面，再叠加 codegraph blast-radius + Grep。无图 → SessionStart/PreToolUse 先 ensure；仍无图则 **deny**，禁止 Grep 当探索主路径。
> serena 写操作会被 `settings.json` 的 `mcp__serena__.*` matcher 纳入验证追踪链；勿绕过。

### 5. 配置变更流程

```
修改常驻 MCP
  → 编辑 .mcp.json（无 plugin 的常驻项）
  → 同步 mcp/servers.json toolsets.always_* 与 mcp-configs/dev.json
  → 同步本文件计数与表格
  → 验证 always_* ⊆ .mcp.json；按需 profile 仅在 mcp-configs/ 声明
  → 重启 Claude Code
```

### 6. 禁止项

- 禁止在 settings.json 中定义 mcpServers（v3.0+）
- 禁止硬编码 API 密钥（使用 ${ENV_VAR} 引用）
- 禁止在 `.mcp.json` 与 `mcp-configs/` 两处维护不同参数定义
- 禁止将按需 profile（debug / fsaccess / ops）服务器默认写入常驻 `.mcp.json`
- 禁止 Agent 自动 merge debug/ops；chrome-devtools / postgres 须中断请用户手动启用
- 禁止同端对同一能力 **plugin + mcp.json 双挂**
- 禁止常驻 `memory` MCP（R18；记忆仅 claude-mem 插件）
- 禁止常驻 `aider-repo-map`、`sequential-thinking`（已删除，不要加回）
- 禁止启用 codebase-memory（全盘索引爆内存）
- 禁止 npx 类服务器不钉版本（R14）

### 7. 按需安装工具

**task-master** — AI 驱动任务管理 MCP（eyaltoledano/claude-task-master）

- 安装：`claude mcp add task-master-ai --scope user --env TASK_MASTER_TOOLS="core" -- npx -y task-master-ai`
- 推荐 core 模式

**codegraph** — 预索引代码知识图谱 MCP（R17 首选）

**codebase-memory** — **已永久禁用（2026-07-31，v10.10）**。架构/ADR/变更影响一律用 `codegraph_explore`。

**firecrawl** — Claude 走 **plugin**（不写 `.mcp.json`）。Cursor 面板无 firecrawl User → 不常驻 MCP。DSH/OpenCode/Qoder 已有则保留钉 `firecrawl-mcp@3.24.0`（各端自管）。

**playwright / chrome-devtools** — 互补（测试 vs 分析联调）。playwright：Claude/Cursor 走 plugin（Cursor UI 核验优先内置浏览器）。chrome-devtools **默认关闭**；需要时**中断请用户手动开 Plugin**，禁止自动 merge debug profile。钉 `@playwright/mcp@0.0.79` / `chrome-devtools-mcp@1.8.0 --isolated`（仅无 plugin 端）。

**架构替代链** — 探索用 `codegraph`（R17）；影响面/风险/审查/PR 用 CRG。

## 双平台工具对照（v11 自 RUNTIME_PLAYBOOK 并入）

| 能力               | Claude Code                         | Cursor                                      |
| ------------------ | ----------------------------------- | ------------------------------------------- |
| 代码探索（怎么运作） | codegraph MCP                     | user-codegraph                              |
| 架构/ADR           | codegraph_explore                   | 同左（cbm 已禁用）                          |
| 精准上下文/影响面/风险/审查/PR | code-review-graph MCP   | user-code-review-graph                      |
| 符号级编辑         | serena MCP                          | user-serena                                 |
| 网页调研           | Firecrawl **plugin**（不写 MCP）    | 面板无 firecrawl User → 不常驻              |
| 搜索               | Exa **plugin**                      | Exa **plugin**                              |
| 文档               | Context7 **plugin**                 | Context7 **plugin**                         |
| 跨仓代码搜索       | grep MCP                            | user-grep                                   |
| GitHub             | plugin 关且无 MCP                   | github Plugin Disabled；PR 用 `gh` CLI      |
| 浏览器测试         | playwright **插件**                 | 内置浏览器（UI 核验）+ playwright plugin（E2E） |
| 浏览器联调         | chrome-devtools **插件默认关；中断启用** | chrome-devtools **plugin 默认 Disabled；中断启用** |

> **OpenCode / DSH**：无 marketplace plugin → context7/exa/playwright 走钉版本 MCP；chrome-devtools 条目保留但默认 disabled。OpenCode github `enabled:false`；DSH github `disabled: true`。均有 CRG、playwright；postgres 默认禁用。无 aider-repo-map / sequential-thinking。firecrawl 若已有则保留。各端 plugin/MCP **自管，禁止经本仓 sync 改开关**。

## 验证清单

```
□ .mcp.json 无 context7/exa/playwright/chrome-devtools/github/firecrawl/memory/aider-repo-map/sequential-thinking
□ servers.json always_* ⊆ .mcp.json
□ settings.json 无 mcpServers；context7/exa/playwright/firecrawl plugin=true；chrome-devtools/github plugin=false（不启用 ralph-loop）
□ Cursor mcp.json 无 plugin 同名 User 条目；无 aider-repo-map/sequential-thinking；postgres disabled 且无明文口令
□ npx 均钉版本
```
