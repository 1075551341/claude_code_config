---
description: Cursor MCP 常驻/按需 + Plugins 边界 — v10.17
---

# Cursor MCP Profile

> 与 [TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md) 互补。Claude Code 权威源：`~/.claude/.mcp.json`（常驻 9，三层架构 v10.17）+ `mcp-configs/` 按需。

## Claude Code 常驻（`.mcp.json`，9 项）

| 层 | MCP | 用途 |
|----|-----|------|
| 本地代码 | codegraph | R17 探索主位（符号/调用链/blast-radius），钉 1.5.0 |
| 本地代码 | code-review-graph | 审查/验证专用图谱（test-gap/风险评分，钉 2.3.6） |
| 本地代码 | aider-repo-map | 仓库级结构概览；codegraph 无索引时的首选降级 |
| 本地代码 | serena | 符号级精确编辑 + LSP 诊断 |
| 远端探索 | github | 官方远端 MCP（`https://api.githubcopilot.com/mcp/`，Bearer `GITHUB_TOKEN`） |
| 远端探索 | grep | grep.app 跨公开仓代码搜索 |
| Web & 文档 | exa | 语义搜索（`EXA_API_KEY`），钉 3.4.0 |
| Web & 文档 | context7 | 库/API 文档 |
| Web & 文档 | firecrawl | 网页抓取（`FIRECRAWL_API_KEY`），钉 3.23.9 |

四工具分工矩阵（何时用 codegraph / aider-repo-map / serena / code-review-graph）→ [rules/MCP.md](../rules/MCP.md) §4。

**浏览器 E2E（Claude）**：`playwright` 走 **Plugins**（`settings.json` enabledPlugins）。**勿**再 merge 进 `.mcp.json`（禁止同端双挂）。

**搜索（Claude）**：exa 已常驻 `.mcp.json`（`EXA_API_KEY` 走 Machine env）。`exa@claude-plugins-official` **保持禁用**（禁与 mcp 双挂）。

**按需 profile**（手动 merge 后重启）：

| Profile | 服务器 | 文件 |
|---------|--------|------|
| debug | chrome-devtools（`@latest` + `--isolated`） | `mcp-configs/debug.json` |
| fsaccess | fs（默认仅配置仓路径） | `mcp-configs/fsaccess.json` |
| ops | redis, sqlite, docker, postgres | `mcp-configs/ops.json` |

> **v10.17 降级**：chrome-devtools 与 fs 退出常驻。fs 是安全性降级——全盘可写会绕过 Edit/Write 验证追踪链，Stop 硬门会误判「本会话未改代码」而放行回归；merge 后由 `mcp__fs__.*` matcher 兜底追踪。

> **codebase-memory 已禁用（2026-07-31）**：根因是 `index_repository` 易对 `C:\Users\<user>` 全盘索引，单进程 >6GB RAM。架构/ADR 场景用 `codegraph_explore`；勿再 merge cbm。

## Cursor 常驻 MCP（`~/.cursor/mcp.json`，恰 8 键）

与 Claude Code 的 9 项对齐，**减 exa**（Cursor 侧 exa 能力由 Exa plugin 提供，禁止同端双挂）。

| MCP               | 用途                                                      |
| ----------------- | --------------------------------------------------------- |
| codegraph         | R17 首选；Guard soft_block Grep/Glob                       |
| code-review-graph | 变更后 test-gap / 风险评分                                 |
| aider-repo-map    | 仓库结构概览 / codegraph 无索引时降级                      |
| serena            | 符号级精确编辑 + LSP 诊断                                  |
| github            | PR/Issue（pr-workflow）                                    |
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
