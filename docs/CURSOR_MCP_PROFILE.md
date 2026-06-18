---
description: Cursor MCP 常驻/按需 + Plugins 边界 — v10.0
---

# Cursor MCP Profile

> 与 [TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md) 互补。Claude Code 权威源：`~/.claude/.mcp.json`（常驻 5）+ `mcp-configs/` 按需。

## Claude Code 常驻（`.mcp.json`）

| MCP | 用途 |
|-----|------|
| codegraph | R17 代码探索首选 |
| crawl | Firecrawl；L2/L3 调研 |
| git | 本地仓库历史/diff |
| fs | 跨路径文件操作 |
| time | 时区/时间（禁 new Date()） |

**按需**（merge `mcp-configs/ops.json` 或 `optional-dev.json`）：redis, sqlite, docker, postgres, chrome-devtools, figma — 见 [rules/MCP.md](../rules/MCP.md)。

## Cursor 常驻 MCP（user）

| MCP | 用途 |
|-----|------|
| user-codegraph | R17 代码探索首选 |
| user-crawl | Firecrawl 网页抓取 |
| user-gh | PR/Issue（pr-workflow） |
| user-pw | E2E/浏览器（按需开） |

## Cursor 已禁用 MCP

| MCP | 原因 |
|-----|------|
| user-postgres | 非默认路径；按需开 |
| user-puppeteer | 与 user-pw 重叠 |
| user-eamodio.gitlens-extension-GitKraken | gh 已覆盖 Git 操作 |
| user-thinking | token 开销高 |
| user-memory | 与 claude-mem 重叠（R18） |
| user-brave | Exa/Firecrawl 已覆盖 |
| user-fetch | crawl 更强 |

## Cursor 常驻 Plugin

| Plugin | 用途 |
|--------|------|
| Superpowers | 五阶段方法论（brainstorming/TDD/verification） |
| Firecrawl | 网页抓取 skill + crawl MCP 配套 |
| Exa | L1/L2 语义搜索 |
| Context7 | L1 库/API 文档 |
| Agent Compatibility | 仓库 agent 兼容性扫描 |

## Cursor 按需 Plugin

| Plugin | 何时开 |
|--------|--------|
| PR Review Canvas | PR 审查 |
| Parallel | parallel-deep-research / 批量提取 |
| CLI for Agents | 写 CLI/自动化脚本 |
| Continual Learning | 长期偏好学习（观察效果） |

## Cursor 已禁用 Plugin

| Plugin | 原因 |
|--------|------|
| compound-engineering | 与 `~/.claude/agents/` gstack 重叠；~10–13K/turn |
| Clerk | 非 Clerk 项目；大量 clerk-* skills |
| Browserstack | 专用跨端测试；日常不需要 |
| Sentry | 未接 Sentry 时纯开销 |
| Create Plugin | 不写插件时；省 plugin-quality-gates 规则 |

## 审查路由

审查仅走 `~/.claude/agents/` gstack（eng/ceo/design/dx/security 等）。MANIFEST `excludes: plugin/compound-engineering/*`。

## Cursor Rules 来源

| 界面项 | 来源 | 控制 |
|--------|------|------|
| User Rules | Settings 文本框 | 4 行指针（[templates/cursor-user-rules-snippet.txt](../templates/cursor-user-rules-snippet.txt)） |
| 00-CLAUDE-ROUTER / CLAUDE / CORE | `sync.ps1` ← `~/.claude` | 源文件去重 |
| CURSOR-EDITOR | cursor-guard 部署 | 保留 |
| AGENTS / WORKFLOW / … | sync lazy rules | glob/智能触发 |
| plugin-* | 已启用插件 | 禁插件即消失 |

## Firecrawl 双入口（C8）

| 平台 | SSOT |
|------|------|
| Cursor | plugin firecrawl skill 优先 |
| Claude Code | user-crawl / crawl MCP |
| fallback | 另一入口 |

## 验证

1. 新 Cursor 会话 Context Usage：固定开销（Skills+Rules+Tools）目标 **≤25K/turn**
2. `check.ps1 -Quick` S3 通过
3. Claude Code：`.mcp.json` 仅 5 个 mcpServers
