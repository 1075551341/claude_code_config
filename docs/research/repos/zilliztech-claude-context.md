# zilliztech/claude-context

> 层: 工具/集成 | 置信度: 中 | 刷新: 2026-06-16

## 核心价值

- Milvus 向量代码索引
- 大 monorepo 语义搜索
- 与 claude-mem 记忆栈互补（代码 vs 会话）

## 证据

- [GitHub zilliztech/claude-context](https://github.com/zilliztech/claude-context)

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| claude_context | `.mcp.json` optional L4 |
| 记忆 SSOT | claude-mem（本仓库不替代） |

## 吸收决策

**L4 按需** — claude-mem SSOT；大 monorepo 显式启用。

## 互博检查

- vs claude-mem：mem=会话记忆；context=代码向量

## v10.1 增量

- 维持 optional；不默认双 MCP 常驻
