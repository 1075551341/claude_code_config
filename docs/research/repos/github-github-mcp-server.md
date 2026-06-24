# github/github-mcp-server v1.2.0

> 层: 工具/集成 | 置信度: 高 | 刷新: 2026-06-24 | 来源: GitHub Releases + newreleases.io + chatforest.com 三源交叉

## 核心价值

- v1.2.0(2026-06-22)：21 toolsets 覆盖 repos/issues/PR/Actions/code_security 等
- v1.0.0(2026-04-16) 首个 major MCP 稳定版；Secret Scanning GA(2026-05-05)
- 54K+ Stars；Go 实现；MIT License
- 远程服务器（GitHub 托管 api.githubcopilot.com/mcp/）+ Docker + 源码三种部署
- MCP Apps（agent 内交互 UI）持续成熟
- GitHub MCP Registry：VS Code 内直接安装 MCP 服务器
- dev 分组按需启用；默认 repos/issues/PR/users/context

## 证据

- [GitHub github/github-mcp-server](https://github.com/github/github-mcp-server)
- v1.2.0(2026-06-22)；v1.0.0(2026-04-16)；54K+ Stars

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| MCP | `.mcp.json` → user-gh / dev 分组 |
| Git 流程 | `skills/git-workflow`, `skills/pr-workflow` |

## 吸收决策

**采纳** — MCP dev 分组；PR 流程 skill L3 按需。

## 互博检查

- vs Shell gh：MCP 优先 GitHub 任务（user rule）

## v10.1 增量

- MCP 接线已验收；docs/TOOL_MATCHING_GUIDE 同步

## v10.3 增量

- Delta 刷新：版本追踪到 v1.2.0；Stars 54K+
- 新增 toolsets：secret_protection / dependabot / copilot / github_support_docs_search
- MCP Apps 交互 UI 持续成熟（remote_mcp_ui_apps feature flag）
- 决策不变：MCP dev 分组按需；PR 流程 skill L3
