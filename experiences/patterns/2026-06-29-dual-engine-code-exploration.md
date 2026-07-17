# 双引擎代码探索模式（codegraph + codebase-memory）

> 日期: 2026-06-29 | 来源: v10.4 ADR | 决策: DeusData/codebase-memory-mcp + colbymchenry/codegraph

## 模式

```
日常符号/调用链/blast-radius  →  codegraph_explore (R17 常驻)
架构全景/ADR/变更风险/跨服务    →  codebase-memory MCP (L4 按需)
二者之后                       →  Grep → Read
```

## 触发条件

启用 codebase-memory（merge `optional-dev.json`）当满足 ≥2：
- 大 monorepo（>500 文件）
- 需 ADR 持久化（`manage_adr`）
- 跨服务链接分析
- git diff 变更风险（`detect_changes`）

## 反模式

- 同一问题同时问 codegraph 与 cbm `search_graph`
- 用 cbm 替代 claude-mem 跨会话记忆（R18）
- 用 Firecrawl 探索本地代码结构

## 运行时（本机已验证 2026-06-29）

- 安装：`npx -y codebase-memory-mcp@0.8.1`（配置在 `optional-dev.json`，按需 merge）
- 索引：`scripts/cbm-index.ps1` → `C-Users-DELL-.claude`（6995 nodes / 9613 edges）
- 抽检：`cli get_architecture` 返回 layers/hotspots/boundaries ✓
- PowerShell 内联 JSON 易转义失败 → 用脚本或 `Get-Content -Raw` 传参

## 归档

claude-context（Milvus）→ archived_redirect；语义搜索用 cbm `semantic_query`。
