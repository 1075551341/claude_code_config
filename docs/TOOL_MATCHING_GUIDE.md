---
description: MCP 语义匹配指南 — 无硬编码 mcp0/mcp1 前缀
---

# MCP 工具语义匹配指南

> **场景→技能/工具/质量门 SSOT** → `config/scenario-router.yaml`。
> **端能力（builtin/plugin/mcp/cli/none + fallback）SSOT** → `config/harness-capabilities.yaml`。
> 本文只留原则、前置条件、禁止项。服务器清单/四工具分工 → `rules/MCP.md`；Cursor 差异 → `docs/CURSOR_MCP_PROFILE.md`。
> 独立审前双图 ensure；并行审查须 inherit、无倍率档。

## 原则

1. **语义优先** — 按意图匹配，非关键词堆砌
2. **Tool-First** — MANIFEST → skill → agent → MCP
3. **memory MCP ≠ claude-mem** — 勿启用 memory MCP；跨会话仅 claude-mem（R18）
4. **本地代码三工具不可互相替代** — 分工见 `rules/MCP.md` §4；禁止用 serena 替代 codegraph 做 R17 探索
5. **工具优先级** — 编辑器内置 > 同名 plugin > MCP > 按需中断启用（chrome-devtools / postgres 禁止自动 merge）

## 前置条件

| 能力                 | 前置                                                                                | 验证                          |
| -------------------- | ----------------------------------------------------------------------------------- | ----------------------------- |
| codegraph 探索 (R17) | SessionStart/PreToolUse ensure：`codegraph init -i` 或 `sync` | `validate_config.py` V16 + 无图 deny |
| code-review-graph    | 同上 ensure：`code-review-graph build` 或 `update`           | 存在 `.code-review-graph/graph.db`   |
| OpenSpec CLI         | `npm i -g @fission-ai/openspec`（Node>=20.19）+ `openspec init --tools cursor`      | `openspec --version`          |
| 深度调研 L3          | 当前 harness 的 `web_scrape` + `web_search`（Firecrawl+Exa，或 fallback）          | 禁止假装双源；Cursor 无 Firecrawl 则 Exa+Context7 |

### Firecrawl 认证

Claude 走 **plugin**（不写 `.mcp.json`），读 Machine env `FIRECRAWL_API_KEY`。Cursor 面板无则不常驻。未配置时 L3 降级为 Exa + Context7。

## 分组与四工具分工（指针）

- 本地代码三工具分工（codegraph / serena / code-review-graph 何时用）→ `rules/MCP.md` §4
- 跨会话记忆仅 claude-mem plugin（R18）；浏览器 Claude=playwright 插件、Cursor=内置浏览器（UI）+ playwright plugin（E2E）；chrome-devtools / postgres 默认关，需要时**中断请用户手动启用**
- 场景→加载列表 → `config/scenario-router.yaml`；调研三档 → 同文件 `research_l1|l2|l3` + `skills/deep-research/SKILL.md`

## 禁止项

- 无双图时 Grep/Glob/编辑/查询 MCP（图谱保鲜硬门）
- 用 serena 替代 codegraph 做 R17；用 codegraph 做 test-gap
- 本地代码用 grep MCP 替代 codegraph
- L3 只用 WebFetch/WebSearch 并声称已双源交叉
- 自动 merge chrome-devtools / postgres profile
- CLAUDE.md 覆盖 OpenCode/DSH `AGENTS.md`

## 决策树（GitHub → `gh` CLI）

```
需要外部信息？
├─ 库/API 文档 → harness lib_docs（Context7）
├─ GitHub 操作 → gh CLI（github Plugin/MCP 默认关）
├─ 跨公开仓找用法 → grep MCP
├─ 网页内容 → harness web_scrape + web_search
├─ 浏览器操作/E2E → Cursor 内置浏览器（UI）；Claude=playwright；E2E=playwright
├─ 性能/调试 → 中断请用户开 chrome-devtools Plugin
├─ 数据库 → 中断请用户设 DATABASE_URL 后启用 postgres
└─ 跨会话回忆 → claude-mem（非 memory MCP）
```

## 跨编辑器 MCP 映射（指针）

- Claude Code 常驻 4（codegraph / CRG / serena / grep）+ 按需 profile → `rules/MCP.md` §2–§3；双平台工具对照 → `rules/MCP.md` §双平台
- Cursor User MCP 4+postgres(disabled) + Plugins → [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)
- capability 解析 → `config/harness-capabilities.yaml`（`.mcp.json` 仍是 Claude Code MCP 服务器权威）

## Shell / Agent Token

- Shell：`pre-rtk-rewrite` hook
- Agent 输出：`skill/caveman-compress`
