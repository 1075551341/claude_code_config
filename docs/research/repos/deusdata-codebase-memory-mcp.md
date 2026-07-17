# DeusData/codebase-memory-mcp v0.8.1

> 层: L3 洞察 | 置信度: 高 | 刷新: 2026-06-29 | 来源: Exa + 官方站 + GitHub Releases v0.8.1 双源交叉
> 仓库: github.com/DeusData/codebase-memory-mcp | 许可证: Apache-2.0 | Stars: 3.3K+

## v10.5 delta (2026-07-17)

- **最新元数据**：32,150 stars；GitHub Release **v0.9.0**；`pushed_at` 2026-07-16T20:29:34Z。
- **自 2026-06-29 的变化**：v0.8.1 后已有 v0.9.0；本轮未发现其改变与 codegraph 的既定双引擎边界。
- **本地吸收**：不变——保持 L4 按需，不进入常驻 MCP；继续作为 `get_architecture`、ADR、跨服务和 `detect_changes` 的首选。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有 Exa 与官方站研究记录。


## v10.5.1 delta (2026-07-17)
- **最新元数据**：32,160★；Release **v0.9.0**（2026-07-08）；`pushed_at` 2026-07-16T20:29:34Z。
- **漂移要点**：一等 Windows 支持；索引 ~61% 更快 + hang supervisor；Graph UI；`detect_changes`/`get_architecture` 加固；提取精度多语言修复。
- **本地吸收 / 缺口**：L4 按需（optional-dev `@0.8.1`）；**场景强制**（架构/ADR/变更）见 v10.5.1 规则补丁；升 0.9 待评估。
- **不吸收**：默认常驻进 Claude `.mcp.json`（Q5=A）。
- **双源**：GitHub API + Firecrawl（v0.9.0）+ Exa。
## 核心价值

- **持久知识图谱 MCP**：将代码库索引为函数、类、调用链、HTTP 路由、跨服务链接的图；agent 查询图而非逐文件读取
- **Token 效率**：官方宣称结构查询约 **120x 更少 token**（5 个结构查询 ~3,400 vs ~412,000 tokens）
- **159 语言** tree-sitter + **9 语言 Hybrid LSP**（Python, TS/JS, PHP, C#, Go, C/C++, Java, Kotlin, Rust）
- **单静态 C 二进制**，零运行时依赖；本地 Nomic `nomic-embed-code` 嵌入（无 API key/Ollama/Docker）
- **14 MCP 工具**：`search_graph`, `trace_path`, `detect_changes`, `query_graph`, `get_architecture`, `manage_adr`, `semantic_query` 等
- **架构智能**：Leiden 社区检测、跨服务 HTTP/gRPC/GraphQL 链接、ADR 持久化、`detect_changes` git diff→符号风险分类
- **安装可审计**：`install --plan` 机器可读收据；支持 Cursor IDE 检测 (#222)

## 14 MCP 工具矩阵

| 类别 | 工具 | 用途 |
|------|------|------|
| 索引 | `index_repository`, `index_status`, `list_projects`, `delete_project` | 构建/更新/管理索引 |
| 查询 | `search_graph`, `trace_path`, `query_graph`, `ingest_traces` | 结构搜索、调用链、Cypher |
| 分析 | `detect_changes`, `get_graph_schema`, `get_architecture` | 变更影响、架构全景 |
| 代码 | `get_code_snippet`, `search_code` | 源码片段、图增强 grep |
| 治理 | `manage_adr` | Architecture Decision Records CRUD |

## 与 codegraph 差异（双引擎互补）

| 维度 | codegraph (R17 常驻) | codebase-memory (L4 按需) |
|------|----------------------|---------------------------|
| 定位 | 符号级日常探索、blast-radius | 架构全景、ADR、跨服务、变更风险 |
| 运行时 | npx `@colbymchenry/codegraph` | 单 C 二进制 |
| 语言 | Tree-sitter 20+ | Tree-sitter 159 + Hybrid LSP 9 |
| 语义搜索 | `codegraph_search` | `semantic_query`（本地嵌入） |
| 独有能力 | MCP watchdog、daemon | ADR、Leiden 聚类、跨 repo、Cypher |
| 加载 | 常驻 5 MCP | L4 optional-dev.json |

## 本地映射

| MANIFEST concern | 路径 | 状态 |
|------------------|------|------|
| codebase_memory_mcp | `mcp-configs/optional-dev.json` | v10.4 新增 |
| 探索链 | `rules/CORE.md` R17 | codegraph 主；cbm 架构/ADR/变更 |
| 启用条件 | `rules/CONTEXT.md` | ≥2 条件显式 merge |
| 跨项目 | `templates/project-init/CLAUDE.md` | index 指引 |

## 吸收决策

**L4 按需** — 与 codegraph 双引擎互补；不进常驻 5 MCP。替代 claude-context 语义搜索位（无 Milvus 依赖）。

启用条件（满足 ≥2）见 `rules/CONTEXT.md`：
1. 大 monorepo（>500 文件）需架构全景
2. 需 ADR 跨会话持久化
3. 跨服务/多 repo 链接分析
4. git diff 变更风险分类（`detect_changes`）

## 互博检查

| 重叠 | 决策 |
|------|------|
| vs codegraph_explore | 日常符号探索 codegraph 优先；cbm 不重复同问 |
| vs claude-context | **archived_redirect** → cbm（v10.4） |
| vs claude-mem | mem=跨会话记忆；cbm=代码结构图，不替代 R18 |
| vs code-explorer agent | cbm 启用时架构任务优先 cbm |

## 吸收优先级

| 优先级 | 内容 |
|--------|------|
| P0 | 调研卡 + MANIFEST concern + optional MCP 配置 |
| P0 | CORE/CONTEXT 双引擎路由 + excludes |
| P1 | project-init 模板 index 指引 |
| P2 | validate_config V17 软警告（cbm 未安装） |

## 证据

- [GitHub Releases v0.8.1](https://github.com/DeusData/codebase-memory-mcp/releases)（npm `codebase-memory-mcp@0.8.1`）
- [官方站 deusdata.github.io/codebase-memory-mcp](https://deusdata.github.io/codebase-memory-mcp/)
- [Exa 交叉验证](https://github.com/DeusData/codebase-memory-mcp)（2026-06-29）

## v10.4 增量

- **新增卡片**：填补 29/29 仓库覆盖缺口
- **决策**：双引擎互补；L4 按需；claude-context archived_redirect
- **安装**：`npx -y codebase-memory-mcp@0.8.1`（Windows 友好）；索引 `scripts/cbm-index.ps1`；merge optional MCP 或 `.mcp.json`
