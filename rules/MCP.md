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

`.mcp.json` 是 MCP 服务器配置的**唯一权威源**。

- 添加服务器 → 只修改 `.mcp.json`
- 删除服务器 → 只修改 `.mcp.json`
- 修改参数 → 只修改 `.mcp.json`
- settings.json 不再重复定义 MCP 服务器（v3.0 起删除冗余）

### 2. 分组视图（v10.0）

`mcp/servers.json` 是 `.mcp.json` 的派生分组视图。

| 分组         | 服务器                                       | 位置                            |
| ------------ | -------------------------------------------- | ------------------------------- |
| always       | codegraph, crawl, git, fs, time              | `.mcp.json`                     |
| ops          | redis, sqlite, docker, postgres              | `mcp-configs/ops.json`          |
| optional-dev | chrome-devtools, figma, exa, codebase-memory | `mcp-configs/optional-dev.json` |

按需 profile 中的 `mcpServers` 块 **手动 merge** 到 `.mcp.json` 后重启 Claude Code。

### 3. 按需启用 ops / optional-dev

1. 打开 `mcp-configs/ops.json` 或 `optional-dev.json`
2. 将 `mcpServers` 对象合并进 `~/.claude/.mcp.json` 的 `mcpServers`
3. 重启 Claude Code
4. 任务完成后可移除并重启（恢复常驻 5）

Cursor 侧见 `docs/CURSOR_MCP_PROFILE.md`（不同步 `.mcp.json`）。

### 4. 配置变更流程

```
修改常驻 MCP
  → 编辑 .mcp.json（仅 always 5）
  → 同步 mcp/servers.json toolsets.always
  → 验证 always ⊆ .mcp.json；ops 仅在 mcp-configs/ 按需 merge
  → 重启 Claude Code
```

### 5. 禁止项

- 禁止在 settings.json 中定义 mcpServers（v3.0+）
- 禁止硬编码 API 密钥（使用 ${ENV_VAR} 引用）
- 禁止在 `.mcp.json` 与 `mcp-configs/` 两处维护不同参数定义（SSOT：profile 文件为按需源，merge 后 `.mcp.json` 为准）
- 禁止将 ops 服务器默认写入常驻 `.mcp.json`（v10 分层）

### 6. 按需安装工具

**task-master** — AI 驱动任务管理 MCP（eyaltoledano/claude-task-master，27K stars）

- 安装：`claude mcp add task-master-ai --scope user --env TASK_MASTER_TOOLS="core" -- npx -y task-master-ai`
- 三级加载：core(7tools,~5K) / standard(15,~10K) / all(36,~21K) — 推荐 core 模式（~70% token 减少）
- Claude Code 模式无需额外 API Key（使用本地实例）
- 功能：PRD解析 → 结构化任务 → 复杂度分析 → 进度追踪

**codegraph** — 预索引代码知识图谱 MCP（R17 首选，v10 mandate）

**codebase-memory** — 代码知识图谱 L4（DeusData/codebase-memory-mcp v0.8.1 钉扎；上游 v0.9.0 待评估）。架构/ADR/变更/跨服务 **场景强制**（v10.5.1）：未调用 → `DONE_WITH_CONCERNS`。Claude：merge `optional-dev` 按需，**不进常驻 5**；Cursor：MCP P0。npx `codebase-memory-mcp@0.8.1`；需先 `scripts/cbm-index.ps1`。

**crawl (Firecrawl)** — `scripts/firecrawl-mcp.ps1` 从系统环境变量读 Key；Cursor `~/.cursor/mcp.json` 同配置

**Understand-Anything** — **v10.5 removed**（ADR-2026-07-17）；审计 catalog 于 `catalog/skills/understand-anything/`；探索替代：codegraph + codebase-memory

## 验证清单

```
□ .mcp.json 包含所有需要的 MCP 服务器
□ servers.json 分组中的服务器名均在 .mcp.json 中存在
□ settings.json 无 mcpServers 定义（v3.0+）
□ 无硬编码 API 密钥
□ CLAUDE_MCP_PROFILE 分组与实际使用一致
```
