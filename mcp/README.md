# MCP 配置指南

> 权威：`.mcp.json`（Claude 常驻 9）+ `mcp/servers.json`（分组视图）+ `docs/CURSOR_MCP_PROFILE.md`（Cursor）
>
> **已废弃**：将 `memory` / `thinking` 当作 core 常驻；启用 codebase-memory；同端 plugin+mcp 双挂（pw/cdt/Cursor 侧 exa）。

## 常驻（Claude `.mcp.json`，9 项三层架构）

| 层 | 服务器 |
|----|--------|
| 本地代码 | codegraph \| code-review-graph \| aider-repo-map \| serena |
| 远端探索 | github \| grep |
| Web & 文档 | exa \| context7 \| firecrawl |

四工具分工（谁做探索、谁做编辑、谁做审查）→ `rules/MCP.md` §4。

认证 env（User 级，已配置）：`GITHUB_TOKEN` + `GITHUB_PERSONAL_ACCESS_TOKEN`（二者同值，后者给 github-mcp-server）/ `EXA_API_KEY` / `FIRECRAWL_API_KEY`。
github MCP 走本地 stdio `~/.local/bin/github-mcp-server.exe`，不要再用 `https://api.githubcopilot.com/mcp/`（Cursor/Claude 会变成 OAuth `mcp_auth` + 0 tools）。

npx 类服务器按 R14 钉版本：codegraph 1.5.0 / firecrawl-mcp 3.23.9 / exa-mcp-server 3.4.0。

## 浏览器

| 能力 | Claude | Cursor |
|------|--------|--------|
| Driving (E2E) | playwright **插件** | 内置 `cursor-ide-browser` |
| Debugging (perf) | 按需 merge `mcp-configs/debug.json` | 内置 `cursor-ide-browser`；确需时按需 merge + `--isolated` |

禁止共享非隔离 profile；禁止与 puppeteer 同开；禁止同端 plugin+mcp 双挂同一能力。

## 记忆

仅 **claude-mem 插件**（R18）。禁止 `memory` MCP。

## 按需（v10.17）

| Profile | 文件 | 说明 |
|---------|------|------|
| debug | `mcp-configs/debug.json` | chrome-devtools（原常驻，v10.17 降级） |
| fsaccess | `mcp-configs/fsaccess.json` | fs（原常驻，v10.17 降级：全盘可写绕过验证追踪链） |
| ops | `mcp-configs/ops.json` | redis / sqlite / docker / postgres |
| collab | `mcp-configs/collab.json` | figma / linear / notion / slack（仅声明） |

`optional-dev.json` 自 v10.17 起不再声明可运行 `mcpServers`，只保留禁用记录与回退说明（cbm 已 disabled/archive）。

## 验证

见 `rules/MCP.md` 验证清单与 `docs/CURSOR_MCP_PROFILE.md`。
