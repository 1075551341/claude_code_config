# Rules 索引

> 源：`rules/` | v13.0.3（6 全量；只保留方向性禁令 + 开发习惯 + 流程补充；流程/审查/完成定义 SSOT → `config/workflow.yaml`）

## alwaysApply — 骨架层

- [CORE.md](rules/CORE.md) — 铁律（方向性禁令）+ 开发习惯 + 工具路由 R17/R18 + 图谱三时点 + 阈值

## trigger: model_decision — 按需补充

- [AGENTS.md](rules/AGENTS.md) — 委派、独立审查路由（spine 渲染）、防互博；模型选择不在本包
- [GIT.md](rules/GIT.md) — Git 分支策略 + Commit 规范 + PR 流程
- [MCP.md](rules/MCP.md) — MCP 服务器配置 SSOT + 分组视图 + 浏览器 UI 测试显式选用 + 编辑器 spawn
- [OPENSPEC.md](rules/OPENSPEC.md) — OpenSpec delta-spec 规范 + /opsx: 命令链
- [SECURITY.md](rules/SECURITY.md) — OWASP Top 10 + 密钥管理 + ML 注入防御

## v13 变更（原全局 → 去向）

| 原 rule | 去向 |
| --- | --- |
| WORKFLOW.md | 删除；五阶段/轨道/完成定义 → `config/workflow.yaml` + `docs/DEV_FLOW.md` |
| CONTEXT.md | 删除；阈值 → `rules/CORE.md`；压缩 → `skills/memory-compression` |
| GOVERNANCE.md | 删除；R14–R16 并入 `rules/CORE.md` 铁律表 |
| FRONTEND.md / BACKEND.md / DATABASE.md | 删除；领域规则按需 → `catalog/rules/RULES_*.md` |
