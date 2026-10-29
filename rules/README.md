# Rules 规则索引

全局 **6 规则文件**（v13：只保留方向性禁令、开发习惯、流程补充）。流程、审查轮次、完成定义的 SSOT 是 `config/workflow.yaml`，不在规则里复述。语言/领域模板在 `catalog/rules/`，按需 Read。

---

## 全局规则（6）

| 文件 | 适用 | 加载 | layer |
|------|------|------|-------|
| `CORE.md` | 铁律 + 开发习惯 + 工具路由 + 图谱三时点 + 阈值 | ✅ alwaysApply | skeleton |
| `AGENTS.md` | 委派、独立审查路由、防互博 | lazy | supplement |
| `GIT.md` | 分支策略（commit → `skills/git-workflow`） | lazy | supplement |
| `MCP.md` | .mcp.json 权威源 + 编辑器 spawn | lazy | supplement |
| `OPENSPEC.md` | OpenSpec delta-spec 规范 + /opsx: 命令链 | lazy | supplement |
| `SECURITY.md` | OWASP、密钥管理 | lazy | supplement |
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

## 同步（多编辑器 1+N）

- **Claude Code**：原生读 `~/.claude/rules/`，零同步。
- **Cursor**：`scripts/sync.ps1` 将 `rules/*.md`（除本 README）+ `CLAUDE.md`（→`00-CLAUDE.mdc`）+ `CURSOR-EDITOR.mdc` 生成实体 `.mdc` 到 local plugin `claude-config`（唯一规则通道，`~/.cursor/rules` 不生效且同名项会被清理）。
- **qoder-cn / trae-cn**：`rules/*.md` 实体复制到 `~/.qoder-cn/rules/*.mdc` 与 `~/.trae-cn/user_rules/*.md`（`.claude-managed` 台账孤儿清除，用户自有规则不受影响）；workbuddy 无规则通道。

清单/常量单源：`config/sync-manifest.json`。源文件变更后重跑 `sync.ps1`（或由 Cursor Guard 自动同步）。
