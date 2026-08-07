# MCP 配置指南

> 权威：`.mcp.json`（Claude 常驻 6）+ `mcp/servers.json`（分组）+ `docs/CURSOR_MCP_PROFILE.md`（Cursor）
>
> **已废弃**：将 `memory` / `thinking` 当作 core 常驻；启用 codebase-memory；同端 plugin+mcp 双挂 pw/cdt。

## 常驻（Claude `.mcp.json`）

codegraph | crawl | fetch | git | fs | time

## 浏览器

| 能力 | Claude | Cursor |
|------|--------|--------|
| Driving (E2E) | playwright **插件** | mcp.json `playwright` + `--isolated` |
| Debugging (perf) | chrome-devtools-mcp **插件** | mcp.json `chrome-devtools` + `--isolated` |

**可同开互补**；禁止共享非隔离 profile；禁止与 puppeteer 同开。

## 记忆

仅 **claude-mem 插件**（R18）。禁止 `memory` MCP。

## 按需

见 `mcp-configs/ops.json`、`optional-dev.json`（cbm 已 disabled/archive）。

## 验证

见 `rules/MCP.md` 验证清单与 `docs/CURSOR_MCP_PROFILE.md`。
