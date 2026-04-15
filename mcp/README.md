# MCP 配置指南

> 本目录包含 MCP (Model Context Protocol) 服务器配置
>
> 整合自：
> - [github/mcp-server](https://github.com/github/mcp-server) - 官方GitHub MCP
> - [zilliztech/claude-context](https://github.com/zilliztech/claude-context) - 上下文增强

---

## 配置格式

### servers.json

主配置文件，定义所有 MCP 服务器连接。

```json
{
  "$schema": "https://modelcontextprotocol.io/schema/2024-11-05/servers",
  "servers": {
    "server-name": {
      "description": "服务器描述",
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {
        "ENV_VAR": "${VALUE}"
      }
    }
  }
}
```

### 服务器类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `command` | 通过命令行启动的本地服务器 | `npx`, `node`, `python` |
| `http` | 远程HTTP服务器 | Exa, 自定义API |

---

## 内置服务器

### github
- **来源**: [github/mcp-server](https://github.com/github/mcp-server)
- **功能**: 代码搜索、PR管理、Issue处理、用户管理
- **认证**: 需要 `GITHUB_TOKEN` 环境变量
- **Toolset**: repos, issues, pull_requests, users, code_search, security

### memory
- **来源**: [@modelcontextprotocol/server-memory](https://github.com/modelcontextprotocol/servers)
- **功能**: 跨会话持久化上下文
- **特性**: 简单键值存储，适合临时记忆

### sequential-thinking
- **来源**: [@modelcontextprotocol/server-sequential-thinking](https://github.com/modelcontextprotocol/servers)
- **功能**: 复杂问题的逐步推理
- **用途**: debug、设计评审、复杂决策

### filesystem
- **来源**: [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers)
- **功能**: 安全文件操作
- **安全**: `ALLOWED_DIRECTORIES` 限制访问范围

### playwright
- **来源**: [@playwright/mcp](https://github.com/microsoft/playwright)
- **功能**: 浏览器自动化和Web测试
- **用途**: E2E测试、Web抓取、UI验证

### exa
- **类型**: HTTP远程服务器
- **功能**: Web搜索和内容提取
- **URL**: `https://mcp.exa.ai/mcp`

### context7
- **来源**: [@upstash/context7-mcp](https://github.com/upstash/context7-mcp)
- **功能**: 代码库上下文增强
- **特性**: AST感知分块、Merkle DAG增量同步

---

## 环境变量

在 `.env` 文件中配置：

```bash
# GitHub认证
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# 其他MCP服务需要的认证
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

---

## MCP 工具集（来自 github/mcp-server）

### repos
- `repos_list` - 列出仓库
- `repos_get` - 获取仓库详情
- `repos_create` - 创建仓库

### issues
- `issues_list` - 列出Issue
- `issues_get` - 获取Issue详情
- `issues_create` - 创建Issue
- `issues_update` - 更新Issue

### pull_requests
- `pulls_list` - 列出PR
- `pulls_get` - 获取PR详情
- `pulls_create` - 创建PR
- `pulls_review` - 审查PR

### users
- `users_get` - 获取用户信息
- `users_list` - 列出用户

### code_search
- `code_search` - 代码搜索
- `code_search_advanced` - 高级搜索

### security
- `security_advisories` - 安全公告
- `secret_scanning` - 密钥扫描

---

## 添加新服务器

1. 在 `servers.json` 的 `servers` 对象中添加新条目
2. 指定 `command` 和 `args`
3. 如需要环境变量，在 `env` 中添加
4. 重启 Claude Code 以加载新配置

---

## 安全注意事项

1. **最小权限**: 只申请需要的权限和作用域
2. **环境变量**: 敏感信息使用环境变量，而非硬编码
3. **Allowed Directories**: filesystem服务器限制访问目录
4. **Token保护**: 不要在日志中打印Token

---

## 远程服务器配置（来自 github/mcp-server）

```json
{
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "X-MCP-Toolsets": "issues,pull_requests",
    "X-MCP-Insiders": "true"
  }
}
```

### Header驱动的动态配置

| Header | 功能 |
|--------|------|
| `X-MCP-Toolsets` | 启用特定工具集 |
| `X-MCP-Tools` | 精确控制可用工具 |
| `X-MCP-Lockdown` | 强制只读安全模式 |

---

## Lockdown 模式

启用只读安全模式：

```json
{
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "X-MCP-Lockdown": "true"
  }
}
```

---

## 版本

- **更新日期**: 2026-04-15
- **整合来源**: github/mcp-server, zilliztech/claude-context
