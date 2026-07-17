---
description: MCP 语义匹配指南 — 无硬编码 mcp0/mcp1 前缀
---

# MCP 工具语义匹配指南

> 与 `mcp-configs/{core,dev,ops}.json` 分组一致。权威源：`.mcp.json`

## 原则

1. **语义优先** — 按意图匹配，非关键词堆砌
2. **Tool-First** — MANIFEST → skill → agent → MCP
3. **memory MCP ≠ claude-mem** — 短期节点 vs 跨会话持久化

## 前置条件（v10.1）

| 能力 | 前置 | 验证 |
|------|------|------|
| codegraph 探索 (R17) | `codegraph init` + `codegraph index` | `validate_config.py` V16 |
| OpenSpec CLI | `npm i -g @fission-ai/openspec`（Node>=20.19）+ `openspec init --tools cursor` | `openspec --version` |
| 深度调研 L3 | Exa + Firecrawl（`FIRECRAWL_API_KEY` 用户环境变量 + `~/.cursor/mcp.json` `${...}`） | MCP 重启后 `firecrawl_search` |

### Firecrawl 认证（Req 6）

`user-crawl` / `.mcp.json` crawl 均依赖 `FIRECRAWL_API_KEY`：

1. 在 [firecrawl.dev](https://firecrawl.dev) 获取 API Key
2. 环境变量：`FIRECRAWL_API_KEY=fc-...`（Windows **用户或系统**环境变量均可）
3. **Cursor/Claude Code**：`crawl` 经 `scripts/firecrawl-mcp.ps1` 启动（从 User/Machine 读 Key；**勿**在 `mcp.json` 写 `${...}` 或占位符）
4. 验证：API 直连 OK → **重启 Cursor MCP** → `firecrawl_search` 成功
5. **未配置时**：L3 降级为 Exa + Context7，报告中标注「Firecrawl 不可用」

## 分组速查（v10.1）

| 分组 | 服务器 | 加载 | 典型场景 |
|------|--------|------|----------|
| always | codegraph, crawl, git, fs, time | `.mcp.json` 常驻 | 探索(R17)、调研、Git、文件、时间 |
| ops | redis, sqlite, docker, postgres | `mcp-configs/ops.json` 按需 | 缓存、DB、容器 |
| optional-dev | chrome-devtools, figma, exa, codebase-memory | `mcp-configs/optional-dev.json` 按需 | 浏览器、设计稿、L4 代码图谱 |
| Cursor 搜索/文档 | Exa, Context7, Firecrawl | plugin + user-crawl | L1–L3 调研 |
| 跨会话记忆 | claude-mem | plugin（非 memory MCP） | R18 |

## 场景 → 工具

| 场景 | 首选 | 备选 |
|------|------|------|
| 代码结构/调用链 (R17) | codegraph_explore（需 `codegraph index`） | Grep → Read |
| 架构全景/ADR/模块边界 (L4) | codebase-memory get_architecture / manage_adr | codegraph explore |
| 变更影响 git diff→符号 (L4) | codebase-memory detect_changes | codegraph_impact |
| 语义找代码 (L4) | codebase-memory semantic_query | Grep |
| OpenSpec 规格变更 | openspec CLI + `/opsx:*` | rules/OPENSPEC.md |
| 项目全貌/领域 | codegraph_explore + Grep | UA（v10 disabled） |
| 查库文档/API (调研 L1) | ctx7 | exa 单次 |
| GitHub PR/Issue | gh | pr-workflow skill |
| 本地 Git 历史 | git | git-workflow skill |
| 网页抓取/搜索 (L2/L3) | crawl + exa | brave |
| 深度调研 (L3) | skills/deep-research | /deep-research |
| E2E/浏览器 | pw | — |
| 跨会话记忆 (R18) | claude-mem plugin | memory MCP（临时节点） |
| 文件读写 | 内置 Read/Write/Grep | fs MCP |
| Shell 命令 | 内置 Bash | — |

## 调研三档（v9.1）

| 档位 | 场景 | 工具链 |
|------|------|--------|
| L1 | 单点事实、API 签名 | Context7 或 Exa 单次 |
| L2 | 方案对比、最佳实践 | Exa + Firecrawl 单页 |
| L3 | 技术选型、/deep-research | Read `skills/deep-research` + Firecrawl + Exa + Context7 |

**前置**：claude-mem search → 项目内代码用 codegraph（R17）；架构/ADR/变更用 codebase-memory（L4，需 index）；禁止先用 Firecrawl 探本地代码。

## 决策树

```
需要外部信息？
├─ 库/API 文档 → ctx7
├─ GitHub 操作 → gh
├─ 网页内容 → crawl 或 fetch
├─ 浏览器交互 → pw
└─ 跨会话回忆 → claude-mem（非 memory MCP 重复存储）
```

## 跨编辑器 MCP 映射（v10.0）

MCP 配置格式不同，无法合并。通过语义匹配桥接：

### Claude Code 常驻（`.mcp.json`）

codegraph | crawl | git | fs | time

### Claude Code 按需（`mcp-configs/`）

| Profile | 服务器 |
|---------|--------|
| ops | redis, sqlite, docker, postgres |
| optional-dev | chrome-devtools, figma, exa, codebase-memory |

### Cursor 常驻（用户已精简）

| 能力 | MCP / Plugin |
|------|----------------|
| 代码探索 | user-codegraph |
| 网页调研 | user-crawl + plugin Firecrawl |
| 搜索 | plugin Exa |
| 文档 | plugin Context7 |
| GitHub | user-gh |
| E2E | user-pw（按需） |

### 已禁用（重叠/低频）

postgres, puppeteer, GitKraken, thinking, brave, memory, fetch — 见 [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)

**规则**：在各编辑器中按意图描述需求，模型自动匹配对应工具。运行时 SSOT → [RUNTIME_PLAYBOOK.md](RUNTIME_PLAYBOOK.md)

## Shell 输出 Token

启用 `pre-rtk-rewrite` hook（RTK 存在则压缩，否则 passthrough）。

## Agent 输出 Token

触发 `skill/caveman-compress`（lite/full/ultra）。
