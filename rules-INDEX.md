# Rules 索引

> 自动生成 | 源：`rules/` | v11.5.0（12 全量；BACKEND/DATABASE 薄层 glob；FRONTEND 去项目特例）

## alwaysApply — 骨架层

- [CORE.md](rules/CORE.md) — 三横切 + 阈值 + 编码规范 + 工程原则 + 铁律 R12-R20 + 图谱三时点 + 变更彻底性

## trigger: model_decision — 按需补充

- [AGENTS.md](rules/AGENTS.md) — 多 Agent 协作、并行审查路由、防互博
- [CONTEXT.md](rules/CONTEXT.md) — 上下文工程 + 三级阈值策略 + 三态制品
- [GIT.md](rules/GIT.md) — Git 分支策略 + Commit 规范 + PR 流程
- [GOVERNANCE.md](rules/GOVERNANCE.md) — 治理详情（R14/R15/R16 适用范围 + 注释模板 + 变更三阶段 + 最佳实践详参）
- [MCP.md](rules/MCP.md) — MCP 服务器配置 SSOT + 分组视图 + 编辑器 spawn
- [OPENSPEC.md](rules/OPENSPEC.md) — OpenSpec delta-spec 规范 + /opsx: 命令链
- [SECURITY.md](rules/SECURITY.md) — OWASP Top 10 + 密钥管理 + ML 注入防御
- [WORKFLOW.md](rules/WORKFLOW.md) — 五阶段工作流 + DAG 编排 + deer-flow

## trigger: glob — 文件匹配

- [FRONTEND.md](rules/FRONTEND.md) — 栈无关前端原则 + 设计系统（不含裸 `*.js`）
- [BACKEND.md](rules/BACKEND.md) — API / 错误处理（`py,go,rs,java,kt,cs` + api/server/backend/services 的 ts/js）
- [DATABASE.md](rules/DATABASE.md) — 表/查询/事务/migration（`sql,prisma` + `**/migrations/**`）
