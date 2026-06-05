---
description: MCP 语义匹配指南 — 无硬编码 mcp0/mcp1 前缀
---

# MCP 工具语义匹配指南

> 与 `mcp-configs/{core,dev,ops}.json` 分组一致。权威源：`.mcp.json`

## 原则

1. **语义优先** — 按意图匹配，非关键词堆砌
2. **Tool-First** — MANIFEST → skill → agent → MCP
3. **memory MCP ≠ claude-mem** — 短期节点 vs 跨会话持久化

## 分组速查

| 分组 | 服务器 | 典型场景 |
|------|--------|----------|
| core | memory, thinking, fs, fetch, time | 记忆、推理、读写文件、HTTP、时间 |
| dev | gh, git, ctx7, pw, crawl, chrome-devtools | GitHub、Git、文档、浏览器 |
| ops | redis, sqlite, docker, postgres, supabase | 缓存、DB、容器 |
| search | brave, exa | 网页/语义搜索 |
| collab | figma, linear, notion, slack | 设计、项目、知识库 |

## 场景 → 工具

| 场景 | 首选 | 备选 |
|------|------|------|
| 查库文档/API | ctx7 | fetch |
| GitHub PR/Issue | gh | — |
| 本地 Git 历史 | git | — |
| 网页抓取/搜索 | crawl / exa / brave | fetch |
| E2E/浏览器 | pw | — |
| 跨会话记忆 | claude-mem plugin | memory MCP（临时节点） |
| 文件读写 | 内置 Read/Write/Grep | fs MCP |
| Shell 命令 | 内置 Bash | — |

## 决策树

```
需要外部信息？
├─ 库/API 文档 → ctx7
├─ GitHub 操作 → gh
├─ 网页内容 → crawl 或 fetch
├─ 浏览器交互 → pw
└─ 跨会话回忆 → claude-mem（非 memory MCP 重复存储）
```

## 跨编辑器 MCP 映射

MCP 配置格式不同，无法合并。通过语义匹配桥接：

| 能力 | Claude Code (.mcp.json) | Cursor (plugin/user) |
|------|------------------------|----------------------|
| 搜索 | brave, exa, perplexity | user-brave, plugin-exa |
| 文档 | ctx7 | plugin-context7 |
| GitHub | gh | user-gh |
| 浏览器 | pw, puppeteer, crawl | user-pw, user-puppeteer, user-crawl |
| 文件 | fs, fetch | user-fs, user-fetch |
| 记忆 | memory | user-memory |
| 推理 | thinking | user-thinking |
| 数据库 | postgres, redis, sqlite | user-postgres |
| Cursor 专有 | — | cursor-app-control, cursor-ide-browser |
| Claude 专有 | docker, chrome-devtools, figma, glif | — |

**规则**：在各编辑器中按意图描述需求，模型自动匹配对应工具。

## Shell 输出 Token

启用 `pre-rtk-rewrite` hook（RTK 存在则压缩，否则 passthrough）。

## Agent 输出 Token

触发 `skill/caveman-compress`（lite/full/ultra）。
