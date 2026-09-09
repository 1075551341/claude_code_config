# Rules 规则索引

全局 **12 规则文件** alwaysApply/lazy/glob（v11.5：BACKEND + DATABASE 薄层 glob；FRONTEND 去项目特例）。语言/领域模板在 `catalog/rules/`，按需通过L0路由Read加载。

---

## 全局规则（12）

| 文件 | 适用 | 加载 | layer |
|------|------|------|-------|
| `CORE.md` | 编码规范 + Karpathy 四原则 + 铁律 R12–R20 + 图谱三时点（R1–R20 见 CLAUDE.md） | ✅ alwaysApply | skeleton |
| `FRONTEND.md` | 栈无关前端原则 + 设计系统（glob：vue/jsx/tsx/css/less/scss/html） | glob | supplement |
| `BACKEND.md` | API / 错误处理（py,go,rs,java,kt,cs + api/server/backend/services 的 ts/js） | glob | supplement |
| `DATABASE.md` | 表/查询/事务/migration（sql,prisma + migrations） | glob | supplement |
| `SECURITY.md` | OWASP、密钥管理 | lazy | supplement |
| `GIT.md` | 分支策略（commit → `skills/git-workflow`） | lazy | supplement |
| `WORKFLOW.md` | discuss→plan→execute→verify→ship + deer-flow 编排 | lazy | supplement |
| `AGENTS.md` | 多 Agent 协作、并行审查路由 | lazy | supplement |
| `MCP.md` | .mcp.json 权威源 + 编辑器 spawn | lazy | supplement |
| `GOVERNANCE.md` | 治理详情 + 最佳实践详参（提示词/API/日志/会话/编排） | lazy | supplement |
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

## 同步（v11.1 多编辑器 1+N）

- **Claude Code**：原生读 `~/.claude/rules/`，零同步。
- **Cursor**：`scripts/sync.ps1` 将 `rules/*.md`（除本 README）+ `CLAUDE.md`（→`00-CLAUDE.mdc`）+ `CURSOR-EDITOR.mdc` 生成实体 `.mdc` 到 local plugin `claude-config`（唯一规则通道，`~/.cursor/rules` 不生效且同名项会被清理）。
- **qoder-cn / trae-cn**（v11.1 恢复）：`rules/*.md` 实体复制到 `~/.qoder-cn/rules/*.mdc` 与 `~/.trae-cn/user_rules/*.md`（`.claude-managed` 台账孤儿清除，用户自有规则不受影响）；workbuddy 无规则通道。

清单/常量单源：`config/sync-manifest.json`。源文件变更后重跑 `sync.ps1`（或由 Cursor Guard 自动同步）。
