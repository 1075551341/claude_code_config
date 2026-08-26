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

### 2. 常驻架构（v10.17）

`.mcp.json` 常驻 **9 项**，三层架构；`mcp/servers.json` 是 `.mcp.json` 的派生分组视图。

| 层         | 服务器                                               | 位置            |
| ---------- | ---------------------------------------------------- | --------------- |
| 本地代码   | codegraph, code-review-graph, aider-repo-map, serena | `.mcp.json`     |
| 远端探索   | github（本地 stdio `github-mcp-server`，User env `GITHUB_PERSONAL_ACCESS_TOKEN`）, grep | `.mcp.json`     |
| Web & 文档 | exa（`EXA_API_KEY`）, context7, firecrawl（`FIRECRAWL_API_KEY`） | `.mcp.json`     |
| debug      | chrome-devtools（`@latest` + `--isolated`，R14 例外，用户决策） | `mcp-configs/debug.json`（按需 merge） |
| fsaccess   | fs（默认仅配置仓路径）                                | `mcp-configs/fsaccess.json`（按需 merge） |
| ops        | redis, sqlite, docker, postgres                      | `mcp-configs/ops.json`（按需 merge） |
| collab     | figma, linear, notion, slack                         | `mcp-configs/collab.json`（**仅声明清单，无 `mcpServers` merge 体**——启用时需自行按官方文档补齐服务器定义） |

按需 profile 中的 `mcpServers` 块 **手动 merge** 到 `.mcp.json` 后重启 Claude Code（collab 除外，见上）。

> **v10.17 降级说明**：`chrome-devtools` 与 `fs` 由常驻降为按需。`fs` 的降级是安全性决策——全盘可写会绕过 Edit/Write 验证追踪链，导致 Stop 硬门误判「本会话未改代码」而放行回归。确需 merge 时，`settings.json` 的 `mcp__fs__.*` matcher 会把写操作纳入追踪。

### 3. 按需启用 profile（debug / fsaccess / ops）

1. 打开对应 `mcp-configs/<profile>.json`
2. 将 `mcpServers` 对象合并进 `~/.claude/.mcp.json` 的 `mcpServers`
3. 重启 Claude Code
4. 任务完成后移除并重启（恢复常驻 9）

> **playwright**：Claude 默认走 **Plugins**，不要 merge 进 `.mcp.json`（禁止同端双挂）。Cursor 侧浏览器能力优先用内置 `cursor-ide-browser`，不必 merge chrome-devtools。详见 CURSOR_MCP_PROFILE。

Cursor 侧见 `docs/CURSOR_MCP_PROFILE.md`（不同步 `.mcp.json`）。Python 系（serena / uv / uvx）经 `scripts/python-mcp.ps1` 启动：清 PYTHONHOME/PYTHONPATH，避免残缺前缀导致 `encodings` 崩溃。编辑器 `mcp.json` 各自手工维护，**禁止经 sync.ps1 复制**。

### 4. 本地代码四工具分工（防互博）

四者能力有重叠，按下表选择；**禁止**用后三者替代 codegraph 做 R17 日常探索。

| 工具              | 定位                                   | 何时用                                                     | 何时不用                            |
| ----------------- | -------------------------------------- | ---------------------------------------------------------- | ----------------------------------- |
| codegraph         | **R17 探索主位**（唯一入口）           | 符号/调用链/依赖/blast-radius/变更前影响面                  | test-gap（无此能力）                |
| aider-repo-map    | 仓库级结构概览（PageRank 排序摘要）    | 陌生仓首屏建立全局印象；**codegraph 无索引时的首选降级**    | 已有 codegraph 索引时的符号级查询   |
| serena            | 符号级精确编辑 + LSP 诊断              | 跨文件重命名/插入/替换符号体、取 `get_diagnostics_for_file` | 只读探索（应走 codegraph）          |
| code-review-graph | **审查/验证专用**（变更后）            | test-gap、`detect_changes` 风险评分、review-delta、pre-merge | 变更前探索（应走 codegraph）        |

> serena 写操作会被 `settings.json` 的 `mcp__serena__.*` matcher 纳入验证追踪链；勿绕过。

### 5. 配置变更流程

```
修改常驻 MCP
  → 编辑 .mcp.json（常驻 9）
  → 同步 mcp/servers.json toolsets.always_* 与 mcp-configs/dev.json
  → 同步本文件计数与表格（v11 起 CURSOR_MCP_PROFILE 仅 Cursor 差异、TOOL_MATCHING_GUIDE 仅匹配矩阵，通常无需改）
  → 验证 always_* ⊆ .mcp.json；按需 profile 仅在 mcp-configs/ 声明
  → 重启 Claude Code
```

### 6. 禁止项

- 禁止在 settings.json 中定义 mcpServers（v3.0+）
- 禁止硬编码 API 密钥（使用 ${ENV_VAR} 引用）
- 禁止在 `.mcp.json` 与 `mcp-configs/` 两处维护不同参数定义
- 禁止将按需 profile（debug / fsaccess / ops）服务器默认写入常驻 `.mcp.json`
- 禁止同端对同一能力 **plugin + mcp.json 双挂**（playwright / chrome-devtools / claude-mem / Cursor 侧 exa）
- 禁止常驻 `memory` / `thinking` MCP（R18 + token；记忆仅 claude-mem 插件）
- 禁止启用 codebase-memory（全盘索引爆内存）
- 禁止 npx 类服务器不钉版本（R14）；`chrome-devtools@latest` 是唯一已记录例外

### 7. 按需安装工具

**task-master** — AI 驱动任务管理 MCP（eyaltoledano/claude-task-master）

- 安装：`claude mcp add task-master-ai --scope user --env TASK_MASTER_TOOLS="core" -- npx -y task-master-ai`
- 推荐 core 模式

**codegraph** — 预索引代码知识图谱 MCP（R17 首选）

**codebase-memory** — **已永久禁用（2026-07-31，v10.10）**。架构/ADR/变更影响一律用 `codegraph_explore`。

**firecrawl** — 常驻键名即 `firecrawl`（历史文档中的 `crawl` 已废弃）；npx 不可用时回退 `scripts/firecrawl-mcp.ps1`，勿两处同时挂载

**playwright / chrome-devtools** — 互补（Driving vs Debugging）；Claude 用插件 / `mcp-configs/debug.json` 按需；Cursor 优先内置 `cursor-ide-browser`

**架构替代链** — 统一 `codegraph`（R17）

## 双平台工具对照（v11 自 RUNTIME_PLAYBOOK 并入）

| 能力           | Claude Code                    | Cursor                             |
| -------------- | ------------------------------ | ---------------------------------- |
| 代码探索       | codegraph MCP                  | user-codegraph                     |
| 架构/ADR       | codegraph_explore              | 同左（cbm 已禁用）                 |
| 变更后审查     | code-review-graph MCP          | user-code-review-graph             |
| 符号级编辑     | serena MCP                     | user-serena                        |
| 网页调研       | firecrawl MCP                  | user-firecrawl / firecrawl skill   |
| 搜索           | exa MCP                        | Exa **plugin**（勿双挂 mcp 条目）  |
| 文档           | context7 MCP                   | user-context7                      |
| 跨仓代码搜索   | grep MCP                       | user-grep                          |
| GitHub         | github MCP（本地 stdio）/ `gh` | user-github                        |
| 浏览器         | playwright **插件**            | 内置 `cursor-ide-browser`          |

> **opencode 侧已知差异**（v11.4.3 查证 opencode 官方文档）：① serena 不传 `--project`（opencode local MCP 无 `${workspaceFolder}` 类占位符，仅 `{env:VAR}` 环境变量替换），项目激活走 serena `activate_project` 工具；② chrome-devtools 默认 `enabled:false`（debug 按需，与 Claude 侧 mcp-configs/debug.json 同语义），临时调试改 true 后用完还原；③ 其余 9 常驻与 `.mcp.json` 同名同钉版本。

## 验证清单

```
□ .mcp.json 恰 9 个常驻（三层架构），无 chrome-devtools/fs/pw/memory/thinking/cbm
□ servers.json toolsets.always_* 与 .mcp.json 一致；按需 profile 仅出现在 on_demand_profiles
□ settings.json 无 mcpServers；CLAUDE_MCP_PROFILE 仅合法值或省略
□ Cursor mcp.json 恰 8 键（9 项减 exa，exa 走 plugin）；无 memory/thinking/claude-mem/exa/postgres
□ 无硬编码 API 密钥（GITHUB_PERSONAL_ACCESS_TOKEN/EXA_API_KEY/FIRECRAWL_API_KEY 走环境变量；github MCP 用本地 stdio，勿把 token 写进 json）
□ npx 类服务器均已钉版本（chrome-devtools@latest 为记录在案的例外）
```
