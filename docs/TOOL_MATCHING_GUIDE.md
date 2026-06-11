---
description: MCP 语义匹配指南 — 无硬编码 mcp0/mcp1 前缀
---

# MCP 工具语义匹配指南

> 与 `mcp-configs/{core,dev,ops}.json` 分组一致。权威源：`.mcp.json`

## 原则

1. **语义优先** — 按意图匹配，非关键词堆砌
2. **Tool-First** — MANIFEST → skill → agent → MCP
3. **memory MCP ≠ claude-mem** — 短期节点 vs 跨会话持久化

## 分组速查（v9.2）

| 分组 | 服务器 | 加载 | 典型场景 |
|------|--------|------|----------|
| always | codegraph, crawl, git, fs, time | `.mcp.json` 常驻 | 探索(R17)、调研、Git、文件、时间 |
| ops | redis, sqlite, docker, postgres | `mcp-configs/ops.json` 按需 | 缓存、DB、容器 |
| optional-dev | chrome-devtools, figma | `mcp-configs/optional-dev.json` 按需 | 浏览器调试、设计稿 |
| Cursor 搜索/文档 | Exa, Context7, Firecrawl | plugin + user-crawl | L1–L3 调研 |
| 跨会话记忆 | claude-mem | plugin（非 memory MCP） | R18 |

## 场景 → 工具

| 场景 | 首选 | 备选 |
|------|------|------|
| 代码结构/调用链 (R17) | codegraph_explore | Grep → Read |
| 项目全貌/领域 | understand-anything | codegraph |
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

**前置**：claude-mem search → 项目内代码用 codegraph（禁止先用 Firecrawl 探本地代码）。

## 决策树

```
需要外部信息？
├─ 库/API 文档 → ctx7
├─ GitHub 操作 → gh
├─ 网页内容 → crawl 或 fetch
├─ 浏览器交互 → pw
└─ 跨会话回忆 → claude-mem（非 memory MCP 重复存储）
```

## 跨编辑器 MCP 映射（v9.2）

MCP 配置格式不同，无法合并。通过语义匹配桥接：

### Claude Code 常驻（`.mcp.json`）

codegraph | crawl | git | fs | time

### Claude Code 按需（`mcp-configs/`）

| Profile | 服务器 |
|---------|--------|
| ops | redis, sqlite, docker, postgres |
| optional-dev | chrome-devtools, figma |

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
