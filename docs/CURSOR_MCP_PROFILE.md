---
description: Cursor MCP 常驻/按需 + Plugins 边界 — v10.12
---

# Cursor MCP Profile

> 与 [TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md) 互补。Claude Code 权威源：`~/.claude/.mcp.json`（常驻 6）+ `mcp-configs/` 按需。

## Claude Code 常驻（`.mcp.json`）

| MCP       | 用途                       |
| --------- | -------------------------- |
| codegraph | R17 代码探索首选           |
| crawl     | Firecrawl；L2/L3 调研      |
| fetch     | 单页抓取转 markdown        |
| git       | 本地仓库历史/diff          |
| fs        | 跨路径文件操作             |
| time      | 时区/时间（禁 new Date()） |

**浏览器（Claude）**：`playwright` + `chrome-devtools-mcp` 走 **Plugins**（`settings.json` enabledPlugins）。**勿**再 merge 进 `.mcp.json`（禁止同端双挂）。

**搜索（Claude）**：user scope `exa` = `npx -y exa-mcp-server` + 环境变量 `EXA_API_KEY`（写入 `~/.claude.json` `mcpServers`，**不**进常驻 `.mcp.json`）。`exa@claude-plugins-official` **保持禁用**（插件 HTTP OAuth 易卡在 Needs authentication，且禁与 mcp 双挂）。`optional-dev.json` 的 exa 条目仅作文档/回退声明。

**按需**（merge `mcp-configs/ops.json` 或 `optional-dev.json`）：redis, sqlite, docker, postgres；chrome-devtools/exa 条目仅为插件不可用时的回退 — 见 [rules/MCP.md](../rules/MCP.md)。

> **codebase-memory 已禁用（2026-07-31）**：根因是 `index_repository` 易对 `C:\Users\<user>` 全盘索引，单进程 >6GB RAM。架构/ADR 场景用 `codegraph_explore`；勿再 merge cbm。

## Cursor 常驻 MCP（`~/.cursor/mcp.json`，恰 7 键）

| MCP              | 用途                                                                 |
| ---------------- | -------------------------------------------------------------------- |
| codegraph        | R17 首选；Guard soft_block Grep/Glob                                 |
| crawl            | Firecrawl（`scripts/firecrawl-mcp.ps1`）                             |
| fetch            | 轻量单页抓取（`scripts/fetch-mcp.ps1`）                               |
| github           | PR/Issue（pr-workflow）                                              |
| fs               | 跨路径文件（配置仓 `~/.claude` + `D:\apdms`）                        |
| playwright       | **Driving**：E2E/跨浏览器；args 含 `--isolated`                      |
| chrome-devtools  | **Debugging**：性能/Lighthouse/网络；args 含 `--isolated`            |

### Playwright ∥ Chrome DevTools（可同开）

二者**不是互斥**，而是互补：

| | Playwright | Chrome DevTools |
|--|------------|-----------------|
| 角色 | Driving（操作、E2E） | Debugging（性能、附着现有 Chrome） |
| 推荐 | 复现/自动化 | 解释慢因、Lighthouse、堆/网络 |

**禁止**：① 同端 plugin + mcp.json 双挂同一能力；② 共享非隔离 Chrome profile（须 `--isolated`）；③ puppeteer + playwright（v10.6 已删 puppeteer）。常驻双开会增加工具 schema token，用文档路由降低误选，而非禁用同开。

## Cursor 已禁用 / 勿写入 mcp.json

| MCP / 能力           | 原因                                      |
| -------------------- | ----------------------------------------- |
| memory               | 与 claude-mem 重叠（R18）；记忆仅走插件   |
| thinking             | token 开销高（逐步 tool call）            |
| claude-mem（mcp 条目） | Cursor 用 plugin 通道；勿与 mcp.json 双开 |
| postgres             | 非默认路径；按需开                        |
| exa（mcp 条目）      | Cursor 用 Exa **plugin**                  |
| ~~puppeteer~~        | 与 playwright 重叠，v10.6 已移除          |

## Cursor 常驻 Plugin

| Plugin              | 用途                       |
| ------------------- | -------------------------- |
| Superpowers         | 五阶段方法论               |
| Firecrawl           | 网页抓取 skill             |
| Exa                 | L1/L2 语义搜索（与 Claude user-scope `exa-mcp-server` + `EXA_API_KEY` 对齐） |
| Context7            | L1 库/API 文档（`resolve-library-id` → `query-docs`） |
| claude-mem          | 跨会话记忆 R18             |
| Agent Compatibility | 仓库 agent 兼容性扫描      |

## Cursor 按需 Plugin

| Plugin             | 何时开                            |
| ------------------ | --------------------------------- |
| PR Review Canvas   | PR 审查                           |
| Parallel           | parallel-deep-research / 批量提取 |
| CLI for Agents     | 写 CLI/自动化脚本                 |
| Continual Learning | 长期偏好学习（观察效果）          |

## Cursor 已禁用 Plugin

| Plugin               | 原因                               |
| -------------------- | ---------------------------------- |
| compound-engineering | 与 `~/.claude/agents/` gstack 重叠 |
| Clerk                | 非 Clerk 项目                      |
| Browserstack         | 专用跨端测试                       |
| Sentry               | 未接 Sentry 时纯开销               |
| Create Plugin        | 不写插件时                         |

## 审查路由

审查仅走 `~/.claude/agents/` gstack。MANIFEST `excludes: plugin/compound-engineering/*`。

## 验证

1. 固定开销目标 **≤25K/turn**（浏览器双开时注意工具误选）
2. `check.ps1 -Quick` S3 通过
3. Claude Code：`.mcp.json` **恰 6** 个 mcpServers（无 pw/cdt）
4. Cursor：`mcp.json` **恰 7** 键；pw/cdt 均含 `--isolated`
5. Guard：`explore.enforce_mode=soft_block`
