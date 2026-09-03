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
| 深度调研 L3          | Exa + Firecrawl（`FIRECRAWL_API_KEY` 用户/系统环境变量）                            | Claude plugin 可用；不写 `.mcp.json` |

### Firecrawl 认证

Claude 走 **plugin**（不写 `.mcp.json`），读 Machine env `FIRECRAWL_API_KEY`。Cursor 面板无则不常驻。未配置时 L3 降级为 Exa + Context7。

## 分组与四工具分工（指针）

- 本地代码三工具分工（codegraph / serena / code-review-graph 何时用）→ `rules/MCP.md` §4
- 跨会话记忆仅 claude-mem plugin（R18）；浏览器 Claude=playwright 插件、Cursor=内置浏览器（UI）+ playwright plugin（E2E）；chrome-devtools / postgres 默认关，需要时**中断请用户手动启用**

## 场景 → 工具

| 场景                        | 首选                                          | 备选                |
| --------------------------- | --------------------------------------------- | ------------------- |
| 代码结构/调用链 (R17)       | codegraph_explore                             | Grep（仅双图就绪后的残留核对） |
| 架构全景/ADR/模块边界       | codegraph_explore                             | 手写 docs/ADR       |
| 精准上下文 / 变更影响       | CRG `get_minimal_context` + `get_impact_radius`（有图） | codegraph blast-radius + Grep |
| 风险门禁 / 审查 / 开 PR     | CRG `detect_changes` + `get_review_context`   | eng-reviewer        |
| 语义找代码                  | codegraph_search                              | grep MCP（跨公开仓）|
| 符号级重命名/替换           | serena `rename_symbol` / `replace_symbol_body` | 内置 Edit + Grep 校验 |
| OpenSpec 规格变更           | openspec CLI + `/opsx:*`                      | rules/OPENSPEC.md   |
| 查库文档/API (L1)           | Context7：`resolve-library-id` → `query-docs` | Exa 单次            |
| GitHub PR/Issue             | `gh` CLI                                      | pr-workflow skill   |
| 本地 Git 历史               | `git` CLI（经 Bash）                          | git-workflow skill  |
| 网页抓取/搜索 (L2/L3)       | firecrawl + Exa（双源交叉）                   | —                   |
| 深度调研 (L3)               | skills/deep-research                          | /deep-research      |
| E2E / 操作浏览器            | Cursor 内置浏览器（UI）；Claude=playwright 插件；E2E 脚本=playwright | — |
| 性能 / Lighthouse           | chrome-devtools（默认关；**中断请用户开 Plugin**，禁止自动 merge debug） | — |
| 数据库                      | postgres（默认关；**中断请用户设 DATABASE_URL 后启用**） | — |
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
├─ 浏览器操作/E2E → Cursor 内置浏览器（UI）；Claude=playwright 插件；E2E 脚本=playwright
├─ 性能/调试 → 中断请用户开 chrome-devtools Plugin（禁止自动 merge debug.json）
├─ 数据库 → 中断请用户设 DATABASE_URL 后启用 postgres
└─ 跨会话回忆 → claude-mem（非 memory MCP）
```

## 跨编辑器 MCP 映射（指针）

- Claude Code 常驻 4（codegraph / CRG / serena / grep）+ 按需 profile → `rules/MCP.md` §2–§3；双平台工具对照 → `rules/MCP.md` §双平台
- Cursor User MCP 4+postgres(disabled) + Plugins → [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)

## Shell / Agent Token

- Shell：`pre-rtk-rewrite` hook
- Agent 输出：`skill/caveman-compress`
