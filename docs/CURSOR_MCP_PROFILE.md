---
description: Cursor MCP 常驻/按需 + Plugins 边界 — v11（仅 Cursor 差异；Claude 侧 SSOT 在 rules/MCP.md）
---

# Cursor MCP Profile

> **本文只保留 Cursor 侧差异**（常驻 8 / 禁用清单 / Plugins）。
> Claude Code 常驻 9 + 按需 profile + 四工具分工 + 禁止项 SSOT → [rules/MCP.md](../rules/MCP.md)；匹配矩阵 → [TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md)（v11 三文档去重）。

> Claude 侧速记：exa 常驻 `.mcp.json`（插件版保持禁用）；playwright 走 Plugins 勿进 `.mcp.json`；chrome-devtools / fs / cbm 状态与理由 → `rules/MCP.md` §2 降级说明。

## Cursor 常驻 MCP（`~/.cursor/mcp.json`，恰 8 键）

与 Claude Code 的 9 项对齐，**减 exa**（Cursor 侧 exa 能力由 Exa plugin 提供，禁止同端双挂）。

| MCP               | 用途                                                      |
| ----------------- | --------------------------------------------------------- |
| codegraph         | R17 首选；Guard soft_block Grep/Glob                       |
| code-review-graph | 变更后 test-gap / 风险评分                                 |
| aider-repo-map    | 仓库结构概览 / codegraph 无索引时降级                      |
| serena            | 符号级精确编辑 + LSP 诊断                                  |
| github            | PR/Issue（本地 stdio `github-mcp-server`，User env `GITHUB_PERSONAL_ACCESS_TOKEN`） |
| grep              | grep.app 跨仓搜索                                          |
| firecrawl         | 网页抓取（`FIRECRAWL_API_KEY`）                            |
| context7          | 库/API 文档                                                |

**浏览器（Cursor）**：优先内置 `cursor-ide-browser`（导航/快照/点击/CDP 一体），不再常驻 playwright 或 chrome-devtools MCP。确需 chrome-devtools 时按需 merge，args 必须含 `--isolated`。

**禁止**：① 同端 plugin + mcp.json 双挂同一能力（exa 是典型）；② 共享非隔离 Chrome profile；③ puppeteer + playwright（v10.6 已删 puppeteer）。

## Cursor 已禁用 / 勿写入 mcp.json

| MCP / 能力           | 原因                                      |
| -------------------- | ----------------------------------------- |
| memory               | 与 claude-mem 重叠（R18）；记忆仅走插件   |
| thinking             | token 开销高（逐步 tool call）            |
| claude-mem（mcp 条目） | Cursor 用 plugin 通道；勿与 mcp.json 双开 |
| postgres             | 非默认路径；按需开                        |
| exa（mcp 条目）      | Cursor 用 Exa **plugin**（v10.17 已移除死条目） |
| chrome-devtools      | v10.17 按需化；优先内置 cursor-ide-browser |
| fs                   | v10.17 按需化；全盘可写绕过验证追踪链      |
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

1. 固定开销目标 **≤25K/turn**
2. `check.ps1 -Quick` S3 通过
3. Claude Code：`.mcp.json` **恰 9** 个 mcpServers（三层架构，无 chrome-devtools/fs/pw 双挂）
4. Cursor：`mcp.json` **恰 8** 键（无 exa 条目，由 plugin 提供）
5. Guard：`explore.enforce_mode=soft_block`
