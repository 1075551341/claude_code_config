# anthropics/claude-plugins-official

> 层: L1 治理(插件分发) | 置信度: 高 | 刷新: 2026-06-19 | 来源: GitHub + claude.com/plugins + 官方 docs 双源
> 许可证: Apache-2.0 | 创建: 2025-11-20 | 主语言: Python

## 核心价值

Anthropic 官方维护的高质量 Claude Code 插件目录（marketplace），是本地多数插件的**分发 SSOT**。

- **双目录结构**：`/plugins`（Anthropic 内部维护）+ `/external_plugins`（合作伙伴/社区，需通过质量+安全审核）
- **安装**：`/plugin install <name>@claude-plugins-official` 或 `/plugin > Discover`
- **社区市场分离**：`anthropics/claude-plugins-community` 独立（commit SHA pinning），与官方市场区分
- **Code intelligence**：11 语言 LSP 族（clangd/csharp/gopls/jdtls/kotlin/lua/php/pyright/rust-analyzer/swift/typescript）按需安装
- 自动可用：Claude Code 启动即挂载官方市场；过期用 `/plugin marketplace update claude-plugins-official`

## 版本与变更

- 滚动更新（无语义版本）；本地按 `gitCommitSha` pinning（见 `plugins/installed_plugins.json`）
- 最近 push 2026-06-19；插件目录持续扩充（含 LSP 族、code-simplifier、pr-review-toolkit、hookify 等）

## 本地集成状态（15 启用 / 3 禁用）

| 插件 | 本地裁决 | 原因 |
|------|----------|------|
| superpowers | ✅ 启用 + local_post_load | 五柱方法论；本地 skills 后加载覆盖 |
| context7 | ✅ 启用 | 技术文档 MCP |
| github | ✅ 启用 | GitHub 集成 |
| firecrawl | ✅ 启用 | L3 外部抓取 |
| feature-dev | ✅ 启用 + MANIFEST excludes | 三 agent 与本地 architect/code-explorer/code-reviewer 互斥 |
| code-review | ✅ 启用 | 与 eng-reviewer 互补（流水线 vs 角色审查） |
| frontend-design | ✅ 启用 | 前端设计 |
| playwright | ✅ 启用 | 浏览器自动化 |
| security-guidance | ✅ 启用 | 安全规则 |
| skill-creator | ✅ 启用 | 技能创建 |
| typescript-lsp | ✅ 启用 | TS LSP（其余 LSP 族按需） |
| chrome-devtools-mcp | ✅ 启用 | Chrome DevTools |
| commit-commands | ✅ 启用 | Git 快捷 |
| claude-mem | ✅ 启用（thedotmack 市场） | 五柱记忆 |
| claude-hud | ✅ 启用 | 状态显示 |
| ralph-loop | ❌ 禁用 | 自动循环与五阶段冲突 |
| claude-code-setup | ❌ 禁用 | 已配置 |
| claude-md-management | ❌ 禁用 | 防自动覆盖 CLAUDE.md |

## 去重决策

| 重叠 | 裁决 |
|------|------|
| feature-dev:code-architect/explorer/reviewer vs 本地 agents | 本地主（MANIFEST excludes 已声明） |
| code-review plugin vs eng-reviewer agent | 互补：plugin 流水线审查；agent 角色审查 |
| compound-engineering（社区）vs gstack 审查 | 禁用 plugin（`[plugin/compound-engineering, gstack_review]`） |
| LSP 族 vs typescript-lsp | 仅启用 typescript-lsp；其余按项目语言 on-demand |

## 吸收优先级

| 优先级 | 内容 |
|--------|------|
| P0 | 作为插件分发 SSOT，installed_plugins.json gitCommitSha pinning（R14 版本克制） |
| P1 | LSP 族按需启用策略（不全量装） |
| 不吸收 | 社区市场批量插件（按需 cherry-pick，防 catalog 膨胀） |

## 证据

- [GitHub anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)（2026-06-19 核验）
- [官方插件目录 claude.com/plugins](https://claude.com/plugins)
- [Discover/install 文档](https://code.claude.com/docs/en/discover-plugins.md)
- 本地 `plugins/installed_plugins.json` + `settings.json` + `plugins/blocklist.json`

## v10.2.1 增量（首次建卡 2026-06-19）

- 补全卡片（此前 27 张未含此卡；现 28 张）——此前仅在 obra-superpowers 安装说明中提及
- 明确官方市场 vs 社区市场（`claude-plugins-community`）分离
- 15 启用 / 3 禁用去重表与 MANIFEST excludes 对齐
