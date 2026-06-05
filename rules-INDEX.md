# Rules 功能速查

| # | Rule | 描述 | 加载 |
|---|------|------|:--:|
| 1 | AGENTS | 多 Agent 协作与互斥规则。触发：并行 Agent、子代理、任务编排。 | 按需 |
| 2 | bestpractice | 综合最佳实践 — 详细参考（骨架内容已迁至 CORE.md） | glob触发 |
| 3 | context-engineering | 上下文工程规则 — 详细策略（骨架内容已迁至 CORE.md） | glob触发 |
| 4 | CORE | 代码开发时始终启用 — 骨架层：编码规范 + 铁律 + 三横切 + 阈值 + 阶段定义 | **必须** |
| 5 | DESIGN | UI/设计项目规范。触发：DESIGN.md、设计系统、design token、UI 规范。 | 按需 |
| 6 | GIT | Git 版本控制、分支管理、提交规范相关任务时启用 | 按需 |
| 7 | MCP | - | 按需 |
| 8 | SECURITY | 安全开发、安全审计、漏洞修复相关任务时启用 | 按需 |
| 9 | workflow | 阶段式工作流规则，定义从讨论到发布的完整开发生命周期 | 按需 |

> 9 rules | 必须=1(CORE) | glob触发+按需=8 | 完整: rules/<name>.md