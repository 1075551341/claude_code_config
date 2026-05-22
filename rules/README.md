# Rules 规则索引

全局 **8 文件** alwaysApply/lazy 规则。语言/领域规则在 `catalog/rules/`，按需复制到项目 `.claude/rules/`。

---

## 全局规则（8）

| 文件 | 适用 | 加载 |
|------|------|------|
| `CORE.md` | 编码规范 + Karpathy 四原则 | ✅ alwaysApply |
| `SECURITY.md` | OWASP、密钥管理 | lazy |
| `GIT.md` | 分支、Commit、PR | lazy |
| `WORKFLOW.md` | discuss→plan→execute→verify→ship | lazy |
| `AGENTS.md` | 多 Agent 协作、互斥 | lazy |
| `MCP.md` | .mcp.json 权威源 | lazy |
| `DESIGN.md` | DESIGN.md token 规范 | lazy |
| `README.md` | 本索引 | — |

---

## 目录规则（catalog/rules/）

语言：PYTHON, TYPESCRIPT, GO, RUST, JAVA, RUBY, CSHARP, DART, MOBILE  
领域：BACKEND, FRONTEND, DATABASE, TESTING, DEVOPS, AI

### 项目级 lazy-load 示例

见 `templates/rules/typescript.lazy.md`

---

## 同步

`scripts/sync.ps1` 软链接 `rules/` → Cursor/Windsurf/Trae
