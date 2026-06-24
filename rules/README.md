# Rules 规则索引

全局 **11 规则文件** alwaysApply/lazy/glob。语言/领域模板在 `catalog/rules/`，按需通过L0路由Read加载。

---

## 全局规则（11）

| 文件 | 适用 | 加载 | layer |
|------|------|------|-------|
| `CORE.md` | 编码规范 + Karpathy 四原则 + 铁律 R12–R19（R1–R19 见 CLAUDE.md） | ✅ alwaysApply | skeleton |
| `FRONTEND.md` | ESLint/Prettier/Stylelint + Vue/React（glob 匹配前端文件） | glob | supplement |
| `SECURITY.md` | OWASP、密钥管理 | lazy | supplement |
| `GIT.md` | 分支策略（commit → `skills/git-workflow`） | lazy | supplement |
| `WORKFLOW.md` | discuss→plan→execute→verify→ship + deer-flow 编排 | lazy | supplement |
| `AGENTS.md` | 多 Agent 协作、互斥 | lazy | supplement |
| `MCP.md` | .mcp.json 权威源 | lazy | supplement |
| `DESIGN.md` | DESIGN.md token 规范 | lazy | supplement |
| `BESTPRACTICE.md` | 错误处理 + 提示词设计 + 代码精炼 + API设计 + 日志规范 | lazy | supplement |
| `CONTEXT.md` | 上下文工程 + 子agent调度 + 腐烂治理 | lazy | supplement |
| `OPENSPEC.md` | OpenSpec delta-spec 规范 + /opsx: 命令链 | lazy | supplement |
| `README.md` | 本索引 | — | — |

---

## 目录规则（catalog/rules/）

语言：PYTHON, TYPESCRIPT, GO, RUST, JAVA, RUBY, CSHARP, DART, MOBILE
领域：BACKEND, FRONTEND, DATABASE, TESTING, DEVOPS, AI

### 按需 lazy-load 示例

| 领域 | 模板 | 完整规则 |
|------|------|----------|
| TypeScript | `templates/rules/typescript.lazy.md` | `catalog/rules/RULES_TYPESCRIPT.md` |
| 前端 | `templates/rules/frontend.lazy.md` | `catalog/rules/RULES_FRONTEND.md` |

---

## 同步

`scripts/sync.ps1` **仅L0入口部署**到各编辑器原生规则目录（v14.5+）：

| 编辑器 | 目标 | L0入口 |
|--------|------|--------|
| Cursor | `~/.cursor/rules/*.mdc` | ROUTER/CLAUDE/CORE/CURSOR-EDITOR |
| Devin | `%APPDATA%\devin\AGENTS.md` + `rules/*.md` | AGENTS.md/ROUTER/CORE |
| Qoder | `~/.qoder/rules/*.mdc` | ROUTER/CLAUDE/CORE/CURSOR-EDITOR |
| Trae | `~/.trae/user_rules/*.md` | ROUTER/CLAUDE/CORE |
| CodeArts | `~/.codeartsdoer/rule/*.mdc` | ROUTER/CLAUDE/CORE |

详细rules通过L0路由按需Read加载。源文件变更后需重新执行 `sync.ps1`。
