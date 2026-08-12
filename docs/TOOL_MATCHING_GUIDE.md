---
description: MCP 语义匹配指南 — 无硬编码 mcp0/mcp1 前缀
---

# MCP 工具语义匹配指南

> 与 `mcp-configs/` 分组一致。权威源：`.mcp.json`（Claude）+ `docs/CURSOR_MCP_PROFILE.md`（Cursor）

## 原则

1. **语义优先** — 按意图匹配，非关键词堆砌
2. **Tool-First** — MANIFEST → skill → agent → MCP
3. **memory MCP ≠ claude-mem** — 勿启用 memory MCP；跨会话仅 claude-mem（R18）
4. **本地代码四工具不可互相替代** — 分工见下节；禁止用 serena/aider-repo-map 替代 codegraph 做 R17 探索

## 前置条件

| 能力                 | 前置                                                                                | 验证                          |
| -------------------- | ----------------------------------------------------------------------------------- | ----------------------------- |
| codegraph 探索 (R17) | `codegraph init` + `codegraph index`                                                | `validate_config.py` V16      |
| code-review-graph    | 项目内 `code-review-graph build` 建图                                                | 存在 `.code-review-graph/`    |
| OpenSpec CLI         | `npm i -g @fission-ai/openspec`（Node>=20.19）+ `openspec init --tools cursor`      | `openspec --version`          |
| 深度调研 L3          | Exa + Firecrawl（`FIRECRAWL_API_KEY` 用户/系统环境变量）                            | MCP 重启后 `firecrawl_search` |

### Firecrawl 认证

常驻键名为 `firecrawl`，读 Machine env `FIRECRAWL_API_KEY`。未配置时 L3 降级为 Exa + Context7。

## 分组速查（v10.17，常驻 9）

| 分组             | 服务器                                                       | 加载                        | 典型场景                |
| ---------------- | ------------------------------------------------------------ | --------------------------- | ----------------------- |
| 本地代码         | codegraph, code-review-graph, aider-repo-map, serena         | `.mcp.json` 常驻            | 结构探索、符号编辑、审查 |
| 远端探索         | github（官方远端+`GITHUB_TOKEN`）, grep                       | `.mcp.json` 常驻            | PR/Issue、跨仓代码搜索  |
| Web & 文档       | exa（`EXA_API_KEY`）, context7, firecrawl（`FIRECRAWL_API_KEY`） | `.mcp.json` 常驻        | L1–L3 调研              |
| debug            | chrome-devtools（`@latest` + `--isolated`）                   | `mcp-configs/debug.json` 按需 | 性能/Lighthouse/网络  |
| fsaccess         | fs（默认仅配置仓路径）                                        | `mcp-configs/fsaccess.json` 按需 | 跨仓批量文件操作   |
| ops              | redis, sqlite, docker, postgres                              | `mcp-configs/ops.json` 按需 | 缓存、DB、容器          |
| 跨会话记忆       | claude-mem                                                   | **仅** plugin               | R18                     |
| 浏览器 E2E       | playwright                                                   | Claude=插件；Cursor=内置 cursor-ide-browser | Driving |

## 本地代码四工具分工

| 工具              | 定位                        | 何时用                                                    | 何时不用                          |
| ----------------- | --------------------------- | --------------------------------------------------------- | --------------------------------- |
| codegraph         | **R17 探索主位**            | 符号/调用链/依赖/blast-radius/变更前影响面                  | test-gap（无此能力）              |
| aider-repo-map    | 仓库级结构概览              | 陌生仓首屏全局印象；**codegraph 无索引时的首选降级**        | 已有索引时的符号级查询            |
| serena            | 符号级精确编辑 + LSP 诊断   | 跨文件重命名/替换符号体、`get_diagnostics_for_file`         | 只读探索（走 codegraph）          |
| code-review-graph | 审查/验证专用（变更后）     | test-gap、`detect_changes` 风险评分、review-delta、pre-merge | 变更前探索（走 codegraph）        |

## 场景 → 工具

| 场景                        | 首选                                          | 备选                |
| --------------------------- | --------------------------------------------- | ------------------- |
| 代码结构/调用链 (R17)       | codegraph_explore                             | aider-repo-map（无索引时） |
| 架构全景/ADR/模块边界       | codegraph_explore                             | 手写 docs/ADR       |
| 变更影响（变更前）          | codegraph_impact / explore blast-radius       | Grep（无索引时）    |
| 变更后 test-gap / 风险评分  | code-review-graph `detect_changes`            | 手工跑测试          |
| 语义找代码                  | codegraph_search                              | grep MCP（跨公开仓）|
| 符号级重命名/替换           | serena `rename_symbol` / `replace_symbol_body` | 内置 Edit + Grep 校验 |
| OpenSpec 规格变更           | openspec CLI + `/opsx:*`                      | rules/OPENSPEC.md   |
| 查库文档/API (L1)           | Context7：`resolve-library-id` → `query-docs` | Exa 单次            |
| GitHub PR/Issue             | github MCP / `gh` CLI                         | pr-workflow skill   |
| 本地 Git 历史               | `git` CLI（经 Bash）                          | git-workflow skill  |
| 网页抓取/搜索 (L2/L3)       | firecrawl + Exa（双源交叉）                   | —                   |
| 深度调研 (L3)               | skills/deep-research                          | /deep-research      |
| E2E / 操作浏览器            | Cursor 内置 cursor-ide-browser；Claude=playwright 插件 | —          |
| 性能 / Lighthouse / 附着会话 | chrome-devtools（按需 merge debug profile）  | —                   |
| 跨会话记忆 (R18)            | claude-mem plugin                             | **勿**用 memory MCP |
| 文件读写                    | 内置 Read/Write/Grep                          | fs MCP（按需 merge）|

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
├─ GitHub 操作 → github MCP / gh
├─ 跨公开仓找用法 → grep MCP
├─ 网页内容 → firecrawl（+ Exa 交叉验证）
├─ 浏览器操作/E2E → Cursor 内置 cursor-ide-browser；Claude=playwright 插件
├─ 性能/调试现有 Chrome → 按需 merge mcp-configs/debug.json
└─ 跨会话回忆 → claude-mem（非 memory MCP）
```

## 跨编辑器 MCP 映射

### Claude Code 常驻（`.mcp.json`，恰 9，三层架构）

本地代码：codegraph | code-review-graph | aider-repo-map | serena
远端探索：github | grep
Web & 文档：exa | context7 | firecrawl

浏览器 E2E：playwright **插件**（勿写入 `.mcp.json`，禁双挂）

### Claude Code 按需（`mcp-configs/`）

| Profile      | 服务器                          |
| ------------ | ------------------------------- |
| debug        | chrome-devtools                 |
| fsaccess     | fs                              |
| ops          | redis, sqlite, docker, postgres |

### Cursor 常驻（`mcp.json`，恰 8）

codegraph | code-review-graph | aider-repo-map | serena | github | grep | firecrawl | context7

exa 走 **Exa plugin**（禁与 mcp 条目双挂）；Plugins：Exa、claude-mem、Firecrawl skill、Superpowers

### 已禁用 / 已按需化

memory、thinking、mcp 条目 claude-mem/exa、postgres 默认、puppeteer、codebase-memory（禁用）；chrome-devtools、fs（v10.17 按需化）— 见 [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)

## Shell / Agent Token

- Shell：`pre-rtk-rewrite` hook
- Agent 输出：`skill/caveman-compress`
