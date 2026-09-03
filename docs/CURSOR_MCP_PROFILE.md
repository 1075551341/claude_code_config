---
description: Cursor MCP 常驻/按需 + Plugins 边界 — plugin 优先（仅 Cursor 差异；Claude 侧 SSOT 在 rules/MCP.md）
---

# Cursor MCP Profile

> **本文只保留 Cursor 侧差异**（User MCP + Plugins）。Claude 侧 SSOT → [rules/MCP.md](../rules/MCP.md)。

> **优先级**：编辑器内置 > 同名 plugin > MCP。同名能力只留 Plugin，禁止写入 `mcp.json`。本文件**不经 sync 改**用户 Plugin 面板或 `mcp.json`。

> **已删除**：`aider-repo-map`、`sequential-thinking`（不要加回 User MCP）。

## Cursor User MCP（`~/.cursor/mcp.json`）

| MCP | 用途 |
| --- | --- |
| codegraph@1.6.0 | R17 探索（怎么运作） |
| code-review-graph==2.3.8 | 精准上下文 / 变更影响 / 风险 / 审查 / PR |
| serena | 符号级精确编辑 + LSP |
| grep | grep.app 跨仓搜索 |
| postgres@0.6.2 | **disabled**；需要时**中断**请用户设 `DATABASE_URL` 后自行启用 |

## Cursor Plugin

| Plugin | 用途 | 面板 |
| --- | --- | --- |
| chrome-devtools | 分析联调 | **默认 Disabled**；需要时中断请用户手动打开 |
| context7 | 库/API 文档 | 开 |
| Exa | 语义搜索 | 开 |
| playwright | E2E 脚本 | 开（UI 核验优先内置浏览器） |
| firecrawl | 网页抓取 | **无此 Plugin**；禁止补 User MCP；L3 `web_scrape` fallback `web_search`（Exa+Context7） |
| github | PR/Issue | **Disabled**（用 `gh` CLI） |

GitKraken User MCP 保持 Disabled，不复制到其他编辑器。

**禁止**：同端 plugin + mcp.json 双挂；明文数据库口令；`@docker/mcp-server`（404）；常驻 aider-repo-map / sequential-thinking；自动 merge debug/ops。
