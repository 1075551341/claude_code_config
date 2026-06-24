# zilliztech/claude-context

> 层: 工具/集成 | 置信度: 中 | 刷新: 2026-06-24 | 来源: GitHub + andrew.ooo + milvus.io 三源交叉

## 核心价值

- 11.4K+ Stars（4 月 9.9K → 6 月 11.4K）；MIT License
- Milvus 向量代码索引；BM25 + Dense Vector 混合检索
- AST 感知分块（Tree-sitter）：16 语言沿语法边界切分
- Merkle Tree 增量索引：仅重新嵌入变更文件
- 实测 ~40% token 减少 + 36.1% 工具调用减少（等质量检索）
- 可插拔嵌入：OpenAI / VoyageAI / Gemini / 本地 Ollama
- 可插拔向量库：自托管 Milvus 或托管 Zilliz Cloud
- MCP 4 工具：index_codebase / search_code / get_indexing_status / clear_index
- 与 claude-mem 记忆栈互补（代码语义 vs 会话记忆）

## 证据

- [GitHub zilliztech/claude-context](https://github.com/zilliztech/claude-context)
- 11.4K+ Stars / 840+ Forks；MIT License；TypeScript

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

## v10.3 增量

- Delta 刷新：Stars 9.9K → 11.4K；实测数据发布（-40% token / -36% 工具调用）
- 架构确认：BM25 + Dense 混合检索 + AST 分块 + Merkle 增量
- 嵌入选项扩展：+ Ollama 本地（零 API 费用，隐私友好）
- 决策不变：L4 按需；claude-mem SSOT；大 monorepo 显式启用
