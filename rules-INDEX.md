# Rules 功能速查

| # | Rule | 描述 | 加载 |
|---|------|------|:--:|
| 1 | CORE | 骨架：编码规范 + 铁律 + 三横切 + 阈值 + 五阶段 | **L0 必须** |
| 2 | AGENTS | 多 Agent 协作与互斥。触发：并行 Agent、子代理、任务编排 | L4 按需 |
| 3 | WORKFLOW | 阶段式工作流 discuss→plan→execute→verify→ship | L4 按需 |
| 4 | SECURITY | 安全开发、审计、漏洞修复 | L4 按需 |
| 5 | OPENSPEC | OpenSpec delta-spec。触发：openspec/、/opsx: | L4 按需 |
| 6 | MCP | MCP 配置；codegraph R17 路由 | L4 按需 |
| 7 | DESIGN | UI/设计规范。触发：DESIGN.md、design token | L4 按需 |
| 8 | CONTEXT | 上下文工程详细策略（骨架在 CORE） | L4 按需 |
| 9 | BESTPRACTICE | 最佳实践详细参考（骨架在 CORE） | L4 按需 |
| 10 | GIT | 分支策略、Git Flow（commit 详规 → skill/git-workflow） | L4 按需 |
| 11 | FRONTEND | ESLint/Prettier/Stylelint + Vue/React 规范 | **L4 glob** |

> 11 rules | L0=1(CORE) | L4 按需=9 | L4 glob=1(FRONTEND) | 源: `rules/<name>.md` → sync → `~/.cursor/rules/<name>.mdc`

## Cursor 规则分层（`~/.cursor/rules/`）

| 类型 | 文件 | 说明 |
|------|------|------|
| L0 alwaysApply | 00-CLAUDE-ROUTER, CLAUDE, CORE, CURSOR-EDITOR | 每轮常驻 |
| L4 intelligently | AGENTS, WORKFLOW, SECURITY, … | Applied intelligently，不占固定 token |
| L4 glob | FRONTEND | 仅编辑 `*.{vue,tsx,jsx,css,…}` 时加载 |

## catalog 领域模板（项目级复制）

| 规则 | 描述 | 全局已同步 |
|------|------|-----------|
| RULES_FRONTEND | 与 `rules/FRONTEND.md` 同源；项目覆盖用 | 是 → FRONTEND.mdc |
| RULES_TYPESCRIPT | TS 类型与工程规范 | 否，复制到项目 |

复制到项目 `.cursor/rules/` 后由 `globs` 触发。勿再手工放全局 `RULES_FRONTEND.md`。
