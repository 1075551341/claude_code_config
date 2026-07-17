# zilliztech/claude-context

> 层: 工具/集成 | 置信度: 中 | 刷新: 2026-06-29 | 来源: GitHub + andrew.ooo + milvus.io 三源交叉
> **status: archived_redirect** | successor: [DeusData/codebase-memory-mcp](deusdata-codebase-memory-mcp.md)


## v10.5.1 delta (2026-07-17)
- **最新元数据**：12,145★；`pushed_at` 2026-07-14。
- **本地映射**：**archived_redirect → cbm**；不启用。
- **来源**：GitHub API（Tier-2）。
## 归档说明（v10.4）

v10.4 起 **claude-context 语义搜索位由 codebase-memory-mcp 替代**：
- claude-context 需 Milvus 基础设施 + 嵌入 API（或 Ollama）
- codebase-memory-mcp 提供本地 `semantic_query`（Nomic 嵌入编译进二进制），零外部依赖
- 本卡保留历史调研数据，**不再作为活跃配置引用**

## 核心价值（历史）

- 11.4K+ Stars（4 月 9.9K → 6 月 11.4K）；MIT License
- Milvus 向量代码索引；BM25 + Dense Vector 混合检索
- AST 感知分块（Tree-sitter）：16 语言沿语法边界切分
- Merkle Tree 增量索引：仅重新嵌入变更文件
- 实测 ~40% token 减少 + 36.1% 工具调用减少（等质量检索）
- 可插拔嵌入：OpenAI / VoyageAI / Gemini / 本地 Ollama
- MCP 4 工具：index_codebase / search_code / get_indexing_status / clear_index

## 证据

- [GitHub zilliztech/claude-context](https://github.com/zilliztech/claude-context)
- 11.4K+ Stars / 840+ Forks；MIT License；TypeScript

## 本地映射（已归档）

| MANIFEST concern | 路径 | 状态 |
|------------------|------|------|
| claude_context_mcp | — | **archived_redirect → codebase_memory_mcp** |
| 记忆 SSOT | claude-mem | 不变 |

## 吸收决策

**archived_redirect** — v10.4 由 codebase-memory-mcp L4 按需替代语义搜索；claude-mem 仍 SSOT。

## 互博检查

- vs claude-mem：mem=会话记忆；context=代码向量（已归档）
- vs codebase-memory：cbm 替代本仓库语义搜索位

## v10.3 增量（历史）

- Delta 刷新：Stars 9.9K → 11.4K；实测 -40% token / -36% 工具调用
- 决策曾维持 L4 按需 — **v10.4 升级为 archived_redirect**

## v10.4 增量

- status → **archived_redirect**
- successor → DeusData/codebase-memory-mcp
- MANIFEST `claude_context_mcp` concern 标记归档；配置引用迁移至 `codebase_memory_mcp`

## v10.5 delta (2026-07-17)

- Stars：12,145；最新 Release：无正式 Release（`gh api`）。
- 保持 archived_redirect → codebase-memory-mcp，无强制集成。
