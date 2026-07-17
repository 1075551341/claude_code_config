---
description: Cursor MCP 常驻/按需 + Plugins 边界 — v10.5
---

# Cursor MCP Profile

> 与 [TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md) 互补。Claude Code 权威源：`~/.claude/.mcp.json`（常驻 5）+ `mcp-configs/` 按需。

## Claude Code 常驻（`.mcp.json`）

| MCP       | 用途                       |
| --------- | -------------------------- |
| codegraph | R17 代码探索首选           |
| crawl     | Firecrawl；L2/L3 调研      |
| git       | 本地仓库历史/diff          |
| fs        | 跨路径文件操作             |
| time      | 时区/时间（禁 new Date()） |

**按需**（merge `mcp-configs/ops.json` 或 `optional-dev.json`）：redis, sqlite, docker, postgres, chrome-devtools, figma, exa, **codebase-memory** — 见 [rules/MCP.md](../rules/MCP.md)。

## Cursor 常驻 MCP（user）

| MCP                  | 用途                                 |
| -------------------- | ------------------------------------ |
| user-codegraph       | R17 首选；Guard soft_block Grep/Glob |
| user-codebase-memory | L4 架构/ADR/变更（P0 推荐启用）      |
| user-crawl           | Firecrawl 网页抓取                   |
| user-gh              | PR/Issue（pr-workflow）              |
| user-pw              | E2E/浏览器（按需开）                 |

## Cursor 已禁用 MCP

| MCP                                      | 原因                      |
| ---------------------------------------- | ------------------------- |
| understand-anything                      | **v10.5 removed**         |
| user-postgres                            | 非默认路径；按需开        |
| user-puppeteer                           | 与 user-pw 重叠           |
| user-eamodio.gitlens-extension-GitKraken | gh 已覆盖 Git 操作        |
| user-thinking                            | token 开销高              |
| user-memory                              | 与 claude-mem 重叠（R18） |
| user-brave                               | Exa/Firecrawl 已覆盖      |
| user-fetch                               | crawl 更强                |

## Cursor 常驻 Plugin

| Plugin              | 用途                       |
| ------------------- | -------------------------- |
| Superpowers         | 五阶段方法论               |
| Firecrawl           | 网页抓取 skill + crawl MCP |
| Exa                 | L1/L2 语义搜索             |
| Context7            | L1 库/API 文档             |
| Agent Compatibility | 仓库 agent 兼容性扫描      |

## Cursor 按需 Plugin

| Plugin             | 何时开                            |
| ------------------ | --------------------------------- |
| PR Review Canvas   | PR 审查                           |
| Parallel           | parallel-deep-research / 批量提取 |
| CLI for Agents     | 写 CLI/自动化脚本                 |
| Continual Learning | 长期偏好学习（观察效果）          |

## Cursor 已禁用 Plugin

| Plugin                      | 原因                                   |
| --------------------------- | -------------------------------------- |
| compound-engineering        | 与 `~/.claude/agents/` gstack 重叠     |
| understand-anything@Lum1104 | **v10.5 removed**（settings 已 false） |
| Clerk                       | 非 Clerk 项目                          |
| Browserstack                | 专用跨端测试                           |
| Sentry                      | 未接 Sentry 时纯开销                   |
| Create Plugin               | 不写插件时                             |

## 审查路由

审查仅走 `~/.claude/agents/` gstack。MANIFEST `excludes: plugin/compound-engineering/*`。

## 验证

1. 固定开销目标 **≤25K/turn**
2. `check.ps1 -Quick` S3 通过
3. Claude Code：`.mcp.json` **仅 5** 个 mcpServers
4. Guard：`explore.enforce_mode=soft_block`
