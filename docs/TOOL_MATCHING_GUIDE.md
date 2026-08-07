---
description: MCP 语义匹配指南 — 无硬编码 mcp0/mcp1 前缀
---

# MCP 工具语义匹配指南

> 与 `mcp-configs/` 分组一致。权威源：`.mcp.json`（Claude）+ `docs/CURSOR_MCP_PROFILE.md`（Cursor）

## 原则

1. **语义优先** — 按意图匹配，非关键词堆砌
2. **Tool-First** — MANIFEST → skill → agent → MCP
3. **memory MCP ≠ claude-mem** — 勿启用 memory MCP；跨会话仅 claude-mem（R18）
4. **Playwright ∥ Chrome DevTools** — 可同开互补（Driving vs Debugging）；须 `--isolated`；禁同端双挂

## 前置条件

| 能力                 | 前置                                                                                | 验证                          |
| -------------------- | ----------------------------------------------------------------------------------- | ----------------------------- |
| codegraph 探索 (R17) | `codegraph init` + `codegraph index`                                                | `validate_config.py` V16      |
| OpenSpec CLI         | `npm i -g @fission-ai/openspec`（Node>=20.19）+ `openspec init --tools cursor`      | `openspec --version`          |
| 深度调研 L3          | Exa + Firecrawl（`FIRECRAWL_API_KEY` 用户/系统环境变量）                            | MCP 重启后 `firecrawl_search` |

### Firecrawl 认证

`crawl` 经 `scripts/firecrawl-mcp.ps1` 读 `FIRECRAWL_API_KEY`。未配置时 L3 降级为 Exa + Context7。

## 分组速查（v10.12）

| 分组             | 服务器                                   | 加载                        | 典型场景                |
| ---------------- | ---------------------------------------- | --------------------------- | ----------------------- |
| always           | codegraph, crawl, fetch, git, fs, time   | `.mcp.json` 常驻 6          | 探索、调研、Git、文件   |
| ops              | redis, sqlite, docker, postgres          | `mcp-configs/ops.json` 按需 | 缓存、DB、容器          |
| optional-dev     | chrome-devtools, exa（回退）             | Claude Exa=user stdio+`EXA_API_KEY`；插件禁用勿双挂 | 浏览器调试、语义搜索  |
| Cursor 搜索/文档 | Exa, Context7, Firecrawl                 | plugin + crawl              | L1–L3 调研              |
| 跨会话记忆       | claude-mem                               | **仅** plugin               | R18                     |
| 浏览器           | playwright + chrome-devtools             | Claude=插件；Cursor=mcp.json+`--isolated` | Driving / Debugging |

## 场景 → 工具

| 场景                        | 首选                                          | 备选                |
| --------------------------- | --------------------------------------------- | ------------------- |
| 代码结构/调用链 (R17)       | codegraph_explore                             | Grep → Read         |
| 架构全景/ADR/模块边界       | codegraph_explore                             | 手写 docs/ADR       |
| 变更影响                    | codegraph_impact / explore blast-radius       | Grep                |
| 语义找代码                  | codegraph_search / Grep                       | —                   |
| OpenSpec 规格变更           | openspec CLI + `/opsx:*`                      | rules/OPENSPEC.md   |
| 查库文档/API (L1)           | Context7：`resolve-library-id` → `query-docs` | Exa 单次            |
| GitHub PR/Issue             | github / gh                                   | pr-workflow skill   |
| 本地 Git 历史               | git                                           | git-workflow skill  |
| 网页抓取/搜索 (L2/L3)       | crawl + Exa                                   | fetch               |
| 深度调研 (L3)               | skills/deep-research                          | /deep-research      |
| E2E / 操作浏览器            | playwright（Driving）                         | —                   |
| 性能 / Lighthouse / 附着会话 | chrome-devtools（Debugging）                 | —                   |
| 跨会话记忆 (R18)            | claude-mem plugin                             | **勿**用 memory MCP |
| 文件读写                    | 内置 Read/Write/Grep                          | fs MCP              |

## 调研三档

| 档位 | 场景               | 工具链                                                   |
| ---- | ------------------ | -------------------------------------------------------- |
| L1   | 单点事实、API 签名 | Context7 或 Exa 单次                                     |
| L2   | 方案对比           | Exa + Firecrawl 单页                                     |
| L3   | 技术选型           | deep-research + Firecrawl + Exa + Context7               |

**前置**：claude-mem search → 项目内代码用 codegraph（R17）；**禁止** codebase-memory；禁止先用 Firecrawl 探本地代码。

## 决策树

```
需要外部信息？
├─ 库/API 文档 → Context7 (resolve-library-id → query-docs)
├─ GitHub 操作 → github/gh
├─ 网页内容 → crawl 或 fetch
├─ 浏览器操作/E2E → playwright
├─ 性能/调试现有 Chrome → chrome-devtools
└─ 跨会话回忆 → claude-mem（非 memory MCP）
```

## 跨编辑器 MCP 映射

### Claude Code 常驻（`.mcp.json`，恰 6）

codegraph | crawl | fetch | git | fs | time

浏览器：playwright + chrome-devtools-mcp **插件**（勿写入 `.mcp.json`）

### Claude Code 按需（`mcp-configs/`）

| Profile      | 服务器                          |
| ------------ | ------------------------------- |
| ops          | redis, sqlite, docker, postgres |
| optional-dev | chrome-devtools, exa（回退）    |

### Cursor 常驻（`mcp.json`，恰 7）

codegraph | crawl | fetch | github | fs | playwright(`--isolated`) | chrome-devtools(`--isolated`)

Plugins：Exa、Context7、claude-mem、Firecrawl skill、Superpowers

### 已禁用

memory、thinking、mcp 条目 claude-mem/exa、postgres 默认、puppeteer、codebase-memory — 见 [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)

## Shell / Agent Token

- Shell：`pre-rtk-rewrite` hook
- Agent 输出：`skill/caveman-compress`
