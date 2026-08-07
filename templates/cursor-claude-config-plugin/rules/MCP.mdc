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

### 2. 分组视图（v10.12）

`mcp/servers.json` 是 `.mcp.json` 的派生分组视图。

| 分组         | 服务器                                 | 位置                              |
| ------------ | -------------------------------------- | --------------------------------- |
| always       | codegraph, crawl, fetch, git, fs, time | `.mcp.json`                       |
| ops          | redis, sqlite, docker, postgres        | `mcp-configs/ops.json`            |
| optional-dev | chrome-devtools, exa                   | `mcp-configs/optional-dev.json`（回退；Claude Exa 现行=user stdio+EXA_API_KEY，插件禁用） |
| collab       | figma, linear, notion, slack           | `mcp-configs/collab.json`（声明） |
| search       | exa                                    | `mcp-configs/search.json`（声明） |

按需 profile 中的 `mcpServers` 块 **手动 merge** 到 `.mcp.json` 后重启 Claude Code。

### 3. 按需启用 ops / optional-dev

1. 打开 `mcp-configs/ops.json` 或 `optional-dev.json`
2. 将 `mcpServers` 对象合并进 `~/.claude/.mcp.json` 的 `mcpServers`
3. 重启 Claude Code
4. 任务完成后可移除并重启（恢复常驻 6）

> **chrome-devtools / playwright**：Claude 默认走 **Plugins**，不要 merge 进 `.mcp.json`（禁止同端双挂）。二者可同开互补（Driving vs Debugging）；同开须 `--isolated`。详见 CURSOR_MCP_PROFILE。

Cursor 侧见 `docs/CURSOR_MCP_PROFILE.md`（不同步 `.mcp.json`）。

### 4. 配置变更流程

```
修改常驻 MCP
  → 编辑 .mcp.json（仅 always 6）
  → 同步 mcp/servers.json toolsets.always
  → 验证 always ⊆ .mcp.json；ops 仅在 mcp-configs/ 按需 merge
  → 重启 Claude Code
```

### 5. 禁止项

- 禁止在 settings.json 中定义 mcpServers（v3.0+）
- 禁止硬编码 API 密钥（使用 ${ENV_VAR} 引用）
- 禁止在 `.mcp.json` 与 `mcp-configs/` 两处维护不同参数定义
- 禁止将 ops 服务器默认写入常驻 `.mcp.json`
- 禁止同端对同一能力 **plugin + mcp.json 双挂**（playwright / chrome-devtools / claude-mem）
- 禁止常驻 `memory` / `thinking` MCP（R18 + token；记忆仅 claude-mem 插件）
- 禁止启用 codebase-memory（全盘索引爆内存）

### 6. 按需安装工具

**task-master** — AI 驱动任务管理 MCP（eyaltoledano/claude-task-master）

- 安装：`claude mcp add task-master-ai --scope user --env TASK_MASTER_TOOLS="core" -- npx -y task-master-ai`
- 推荐 core 模式

**codegraph** — 预索引代码知识图谱 MCP（R17 首选）

**codebase-memory** — **已永久禁用（2026-07-31，v10.10）**。架构/ADR/变更影响一律用 `codegraph_explore`。

**crawl (Firecrawl)** — `scripts/firecrawl-mcp.ps1`；Cursor `mcp.json` 同配置

**playwright / chrome-devtools** — 互补可同开；Claude 用插件；Cursor mcp.json 写两键且 `--isolated`

**架构替代链** — 统一 `codegraph`（R17）

## 验证清单

```
□ .mcp.json 恰 6 个常驻（含 crawl+fetch），无 pw/cdt/memory/thinking
□ servers.json toolsets.always 与 .mcp.json 一致
□ settings.json 无 mcpServers；CLAUDE_MCP_PROFILE 仅合法值或省略
□ Cursor mcp.json 恰 7 键；pw/cdt 含 --isolated；无 memory/thinking/claude-mem/exa/postgres
□ 无硬编码 API 密钥
```
