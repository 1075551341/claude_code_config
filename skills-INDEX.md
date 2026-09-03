# Skills 索引

> 自动生成 | 源：`skills/` | 分级来自 MANIFEST loading_tiers | v11.4.15（36 全量 = L1×4 + L2×5 + L3×27；catalog 变体见 `catalog/INDEX.md`）

## L1 — 会话常驻 (4)

- [using-superpowers](skills/using-superpowers/SKILL.md) — 技能发现与 Tool-First 路由
- [change-impact-analysis](skills/change-impact-analysis/SKILL.md) — 变更影响分析，改前必执行
- [brainstorming](skills/brainstorming/SKILL.md) — HARD-GATE 方案设计（非简单任务必加载）
- [task-triage](skills/task-triage/SKILL.md) — 判定 SSOT：Phase0盘点；简单=关联需改≤2+白名单+六维全低+模型匹配低+attempt=1（缺一不可）；持续处理执行升档；非简单先 grill；完成前均须验证

## L2 — 阶段门控 (5)

| 阶段  | Skill                                                                            | 触发               |
| ----- | -------------------------------------------------------------------------------- | ------------------ |
| 2规格 | [writing-plans](skills/writing-plans/SKILL.md)                                   | 原子级实施计划     |
| 2规格 | [spec-validation](skills/spec-validation/SKILL.md)                               | spec可验证验收标准 |
| 3执行 | [executing-plans](skills/executing-plans/SKILL.md)                               | 按计划逐步执行     |
| 3调试 | [systematic-debugging](skills/systematic-debugging/SKILL.md)                     | 根因分析/5Why      |
| 4验证 | [verification-before-completion](skills/verification-before-completion/SKILL.md) | 完成前交叉验证     |

## L3 — 信号触发 (27)

### 显式触发工作流（v10.15 起默认关闭，仅用户明确要求时启用）

- [test-driven-development](skills/test-driven-development/SKILL.md) — RED-GREEN-REFACTOR（loading_tier: L3）
- [subagent-driven-development](skills/subagent-driven-development/SKILL.md) — 子Agent两阶段审查（loading_tier: L3）

### 调研与决策

- [deep-research](skills/deep-research/SKILL.md) — L3 深度调研（Firecrawl+Exa+V1-V5验证）
- [adr-management](skills/adr-management/SKILL.md) — 架构决策记录管理

### 审查与质量

- [requesting-code-review](skills/requesting-code-review/SKILL.md) — 请求代码审查
- [receiving-code-review](skills/receiving-code-review/SKILL.md) — 接收审查反馈
- [autoplan](skills/autoplan/SKILL.md) — 自动CEO-Design-Eng审查流水线

### 设计与UI

- [design-pipeline](skills/design-pipeline/SKILL.md) — 设计管线（探索-对比板-HTML；v11 并入 design-engineer Phase 2）

### 上下文与记忆

- [memory-compression](skills/memory-compression/SKILL.md) — 上下文压缩与跨会话记忆
- [claude-mem-maintenance](skills/claude-mem-maintenance/SKILL.md) — claude-mem 记忆维护

### 代码架构

- [improve-codebase-architecture](skills/improve-codebase-architecture/SKILL.md) — 代码库架构改进
- [karpathy-guidelines](skills/karpathy-guidelines/SKILL.md) — Karpathy 四原则
- [structured-artifacts](skills/structured-artifacts/SKILL.md) — GSD 结构化制品管理

### 重构与技能治理

- [code-refactoring](skills/code-refactoring/SKILL.md) — 行为保持重构（圈复杂度/坏味道/安全重构；v11 并入前端提案模式）
- [frontend-library-advisor](skills/frontend-library-advisor/SKILL.md) — 前端 npm 库选型推荐
- [frontend-design-pattern-applier](skills/frontend-design-pattern-applier/SKILL.md) — 前端坏味道→设计模式重构
- [skill-creator](skills/skill-creator/SKILL.md) — 创建/更新有效技能指南
- [skill-reviewer](skills/skill-reviewer/SKILL.md) — skill 合规性审查
- [test-edge-case-analyzer](skills/test-edge-case-analyzer/SKILL.md) — 边界测试场景发现

### 执行与编排

- [workstream-management](skills/workstream-management/SKILL.md) — 并行任务流管理（git worktree）
- [using-git-worktrees](skills/using-git-worktrees/SKILL.md) — Git Worktree 并行开发

### Git与发布

- [git-workflow](skills/git-workflow/SKILL.md) — Git 工作流
- [pr-workflow](skills/pr-workflow/SKILL.md) — PR 工作流
- [ship](skills/ship/SKILL.md) — 发布管线（v11 并入 release-engineer）
- [finishing-a-development-branch](skills/finishing-a-development-branch/SKILL.md) — 开发分支完成处理

### 优化与学习

- [caveman-compress](skills/caveman-compress/SKILL.md) — 输出压缩（caveman模式）

### 导航与引导

- [triage](skills/triage/SKILL.md) — Bug分类（P0-P3）

## v11 变更（原全局 → 去向）

| 原 skill                                                                                             | 去向                                                                    |
| ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| office-hours / instinct-learning / onboarding-guide / claude-to-deerflow / browser-qa / taste-memory | 降级 `catalog/skills/`（按需复制进项目）                                |
| context-engineering                                                                                  | 删除（正文并入 `rules/CONTEXT.md`）                                     |
| frontend-refactor-proposer                                                                           | 并入 `skills/code-refactoring/`（子文档 frontend-refactor-proposal.md） |
| writing-skills                                                                                       | 并入 `skills/skill-creator/`（前言：技能编写元理念）                    |

> superpowers 系 13 技能（brainstorming/writing-plans/…）为本地深度定制版（五阶段/门控/verify_tier 集成，相似度<10%），**保留本地权威**，插件版仅作上游参考。
