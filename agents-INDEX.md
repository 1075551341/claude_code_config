# Agents 功能速查

| # | Agent | 描述 | 加载 |
|---|-------|------|:--:|
| 1 | agentic-orchestrator | 多 Agent 并行编排。触发词：并行 Agent、子代理、任务编排、orchestrator。 | **必须** |
| 2 | architect | 系统架构设计。触发词：架构设计、技术选型、系统设计、architecture。 | **必须** |
| 3 | build-error-resolver | 构建/编译/类型错误修复。触发词：build error、编译错误、类型错误、依赖冲突。 | **必须** |
| 4 | ceo-reviewer | 产品决策审查（大功能/新特性时启用）。触发词：产品审查、scope审查、用户价值、ceo review。 | 审查时 |
| 5 | code-explorer | 只读代码探索。触发词：探索代码库、理解架构、追踪调用链、where is。 | **必须** |
| 6 | code-reviewer | 代码审查。触发词：代码审查、PR审查、review。审查不改代码。 | **必须** |
| 7 | codex-reviewer | Codex 跨模型独立审查 — 从不同模型视角发现 Claude 盲点（gstack /codex） | v0.19 |
| 8 | cso | 安全总管，执行 OWASP Top 10 + STRIDE 威胁建模审计 | 补充 |
| 9 | design-engineer | 设计工程师，将 mockup 转化为生产级 HTML/CSS，检测框架适配 | 补充 |
| 10 | designer | UI/UX 审查（UI/交互变更时启用）。触发词：设计审查、UI审查、交互审查、design review。 | 审查时 |
| 11 | doc-writer | 技术文档工程师，更新项目文档匹配代码变更，构建 Diataxis 覆盖图 | 补充 |
| 12 | eng-reviewer | 工程审查（所有变更必须通过）。触发词：eng review、代码审查、PR审查、工程评审。 | 审查时 |
| 13 | ios-specialist | iOS 专用审查 — QA测试/fix修复/design-review设计审查/clean清理/sync同步（gstack v0. | v0.19 |
| 14 | performance-engineer | 性能工程师，基准页面加载、Core Web Vitals、资源大小，PR前后对比 | 补充 |
| 15 | planner | 薄编排：调用 writing-plans skill 产出实施计划。触发词：写计划、任务分解、实施计划、writing plans | **必须** |
| 16 | product-manager | 产品经理，执行六问框架重新定义产品问题，挑战前提，生成实现方案 | 补充 |
| 17 | qa | 质量保障审查（测试用例、边界、回归）。触发词：QA审查、测试审查、边界测试、回归测试。 | 审查时 |
| 18 | release-engineer | 发布工程师，负责同步main、运行测试、审计覆盖、推送、开PR | 补充 |
| 19 | security-reviewer | 安全审查（安全敏感变更时启用）。触发词：安全审查、漏洞检测、OWASP、安全审计、代码安全。 | 审查时 |
| 20 | spec-reviewer | 规格/计划文档审查。触发词：审查 spec、审查计划、doc review。 | **必须** |
| 21 | sre | 站点可靠性工程师，负责 canary 监控、部署后验证、性能回归检测 | 补充 |

> 21 agents | 必须=7 | 审查=5 | 补充=7+v0.19=2 | 完整: agents/<name>.md