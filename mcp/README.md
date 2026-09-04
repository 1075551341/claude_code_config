# MCP 配置指南

> 权威：`.mcp.json`（Claude 常驻：codegraph / CRG / serena / grep）+ `mcp/servers.json`（分组视图）+ `docs/CURSOR_MCP_PROFILE.md`（Cursor）
>
> **优先级**：编辑器内置 > 同名 plugin > MCP > 按需中断启用。
> **已删除**：`aider-repo-map`、`sequential-thinking`。禁止常驻 `memory` MCP；禁止 codebase-memory；禁止同端 plugin+mcp 双挂。

## 常驻（Claude `.mcp.json`）

| 层 | 服务器 |
|----|--------|
| 本地代码 | codegraph \| code-review-graph \| serena |
| 远端探索 | grep |

三工具分工 → `skills/mcp-config/SKILL.md`（CRG = 精准上下文/影响面/风险/审查/PR）。

context7 / exa / playwright / firecrawl 走 Claude Plugins。chrome-devtools plugin **默认 false**。github 不常驻。

## 浏览器

| 能力 | Claude | Cursor |
|------|--------|--------|
| Driving (E2E) | playwright **插件** | 内置浏览器（UI）+ playwright plugin（E2E） |
| Debugging (perf) | chrome-devtools **默认关；中断请用户开 Plugin** | 同左 |

禁止自动 merge `mcp-configs/debug.json`。仅用户确认且 Plugin 不可用时才由用户 merge（须 `--isolated`）。禁止与 plugin 双挂。

## 记忆

仅 **claude-mem 插件**（R18）。禁止 `memory` MCP。

## 按需（v10.17；v11.4.5 中断启用）

| Profile | 文件 | 说明 |
|---------|------|------|
| debug | `mcp-configs/debug.json` | chrome-devtools（Agent 禁止自动 merge） |
| fsaccess | `mcp-configs/fsaccess.json` | fs |
| ops | `mcp-configs/ops.json` | redis / sqlite / docker / postgres（postgres 中断启用） |
| collab | `mcp-configs/collab.json` | figma / linear / notion / slack（仅声明） |

`optional-dev.json` 自 v10.17 起不再声明可运行 `mcpServers`，只保留禁用记录与回退说明（cbm 已 disabled/archive）。

## 验证

见 `skills/mcp-config/SKILL.md` 验证清单与 `docs/CURSOR_MCP_PROFILE.md`。
