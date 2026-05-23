# Rules 规则索引

全局 **10 文件** alwaysApply/lazy 规则。语言/领域规则在 `catalog/rules/`，按需复制到项目 `.claude/rules/`。

---

## 全局规则（10）

| 文件 | 适用 | 加载 | layer |
|------|------|------|-------|
| `CORE.md` | 编码规范 + Karpathy 四原则 + 铁律 R1-R11 | ✅ alwaysApply | skeleton |
| `SECURITY.md` | OWASP、密钥管理 | lazy | supplement |
| `GIT.md` | 分支、Commit、PR | lazy | supplement |
| `WORKFLOW.md` | discuss→plan→execute→verify→ship + deer-flow 编排 | lazy | supplement |
| `AGENTS.md` | 多 Agent 协作、互斥 | lazy | supplement |
| `MCP.md` | .mcp.json 权威源 | lazy | supplement |
| `DESIGN.md` | DESIGN.md token 规范 | lazy | supplement |
| `BESTPRACTICE.md` | 错误处理 + 提示词设计 + 代码精炼 + API设计 + 日志规范 | lazy | supplement |
| `CONTEXT.md` | 上下文工程 + 子agent调度 + 腐烂治理 | lazy | supplement |
| `README.md` | 本索引 | — | — |

---

## 目录规则（catalog/rules/）

语言：PYTHON, TYPESCRIPT, GO, RUST, JAVA, RUBY, CSHARP, DART, MOBILE  
领域：BACKEND, FRONTEND, DATABASE, TESTING, DEVOPS, AI

### 项目级 lazy-load 示例

见 `templates/rules/typescript.lazy.md`

---

## 同步

`scripts/sync.ps1` **格式转换复制**（非软链接）到各编辑器原生规则目录：

| 编辑器 | 目标 |
|--------|------|
| Cursor | `~/.cursor/rules/*.mdc` |
| Windsurf | `~/.windsurf/rules/*.md` + `global_rules.md`（仅 CLAUDE.md 精简） |
| Trae | `~/.trae/user_rules/*.md` |

源文件变更后需重新执行 `sync.ps1`。
