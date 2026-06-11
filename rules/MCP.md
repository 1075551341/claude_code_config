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

### 2. 分组视图（v9.2）

`mcp/servers.json` 是 `.mcp.json` 的派生分组视图。

| 分组 | 服务器 | 位置 |
|------|--------|------|
| always | codegraph, crawl, git, fs, time | `.mcp.json` |
| ops | redis, sqlite, docker, postgres | `mcp-configs/ops.json` |
| optional-dev | chrome-devtools, figma | `mcp-configs/optional-dev.json` |

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
- 禁止将 ops 服务器默认写入常驻 `.mcp.json`（v9.2 分层）

### 6. 按需安装工具

**task-master** — AI 驱动任务管理 MCP（eyaltoledano/claude-task-master，27K stars）
- 安装：`claude mcp add task-master-ai --scope user --env TASK_MASTER_TOOLS="core" -- npx -y task-master-ai`
- 三级加载：core(7tools,~5K) / standard(15,~10K) / all(36,~21K) — 推荐 core 模式（~70% token 减少）
- Claude Code 模式无需额外 API Key（使用本地实例）
- 功能：PRD解析 → 结构化任务 → 复杂度分析 → 进度追踪

**codegraph** — 预索引代码知识图谱 MCP（colbymchenry/codegraph）
- 安装：`npx @colbymchenry/codegraph` → `codegraph init -i`
- 已注册到 .mcp.json，按需启用
- 效果：~35% token 节省，~70% 工具调用减少，100% 本地
- 20+ 语言 + 14 框架路由识别 + iOS/RN 跨语言桥接
- MCP 工具：codegraph_search | context | trace | callers | callees | impact | node | explore | files | status
- 文件监听自动增量同步，无需手动 `codegraph sync`

**Understand-Anything** — 交互式代码知识图（Lum1104/Understand-Anything）
- 安装：`/plugin marketplace add Lum1104/Understand-Anything` → `/plugin install understand-anything`
- 命令：`/understand`（分析构建知识图）、`/understand-dashboard`（可视化面板）、`/understand-chat`（自然语言问答）、`/understand-diff`（变更影响分析）、`/understand-explain`（文件/函数深读）、`/understand-onboard`（新成员入门指南）、`/understand-domain`（业务领域提取）、`/understand-knowledge`（Wiki 知识图）
- 多 Agent 管线：project-scanner → file-analyzer → architecture-analyzer → tour-builder → graph-reviewer → domain-analyzer
- 团队共享：提交 `.understand-anything/knowledge-graph.json`，队友跳过分析管线
- 增量更新：`/understand --auto-update` 通过 post-commit hook 自动补丁

## 验证清单

```
□ .mcp.json 包含所有需要的 MCP 服务器
□ servers.json 分组中的服务器名均在 .mcp.json 中存在
□ settings.json 无 mcpServers 定义（v3.0+）
□ 无硬编码 API 密钥
□ CLAUDE_MCP_PROFILE 分组与实际使用一致
```
