# MCP 服务器配置规范

## 适用场景
- 修改 MCP 服务器配置
- 添加/删除 MCP 服务器
- 验证 MCP 配置一致性

## 核心规则

### 1. 单一权威源

`.mcp.json` 是 MCP 服务器配置的唯一权威源。

- 添加服务器 → 只修改 `.mcp.json`
- 删除服务器 → 只修改 `.mcp.json`
- 修改参数 → 只修改 `.mcp.json`

### 2. 分组视图

`mcp/servers.json` 是 `.mcp.json` 的派生分组视图，仅包含 toolset 分组映射。

```json
{
  "toolsets": {
    "core": ["memory", "thinking", "fs", "fetch", "time"],
    "dev": ["gh", "git", "ctx7", "pw", "crawl"],
    "ops": ["redis", "sqlite", "docker", "postgres", "supabase"],
    "search": ["brave", "exa"],
    "collab": ["figma", "linear", "notion", "slack"]
  }
}
```

- servers.json 中的服务器名必须在 .mcp.json 中存在
- servers.json 不重复服务器参数定义

### 3. 运行时覆盖

`settings.json` 中 `mcpServers` 仅保留需要运行时环境覆盖的条目。

- 不与 .mcp.json 重复定义同一服务器
- 仅当需要覆盖 env 时才在 settings.json 中添加条目

### 4. 配置变更流程

```
修改 MCP 配置
  → 编辑 .mcp.json
  → 更新 mcp/servers.json 分组映射（如需）
  → 验证一致性（servers.json 中服务器均在 .mcp.json 中）
  → 重启 Claude Code
```

### 5. 禁止项

- 禁止在三处配置中定义同一服务器但参数不一致
- 禁止在 settings.json mcpServers 中硬编码 API 密钥
- 禁止删除 .mcp.json 中的服务器而不更新 servers.json 分组映射

## 验证清单

```
□ .mcp.json 包含所有需要的 MCP 服务器
□ servers.json 分组中的服务器名均在 .mcp.json 中存在
□ settings.json mcpServers 无与 .mcp.json 重复的完整定义
□ 同一服务器在三处配置中参数一致
□ 无硬编码 API 密钥
```
