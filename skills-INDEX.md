# Skills 索引

> 自动生成 | 源：`skills/` | 分级来自 MANIFEST loading_tiers | v10.17.0（45 全量）

## L1 — 会话常驻 (4)

- [using-superpowers](skills/using-superpowers/SKILL.md) — 技能发现与 Tool-First 路由
- [change-impact-analysis](skills/change-impact-analysis/SKILL.md) — 变更影响分析，改前必执行
- [brainstorming](skills/brainstorming/SKILL.md) — HARD-GATE 方案设计（非简单任务必加载）
- [task-triage](skills/task-triage/SKILL.md) — 判定 SSOT：Phase0盘点；简单=关联需改≤2+白名单+六维全低+模型匹配低+attempt=1（缺一不可）；持续处理执行升档；非简单先 grill；完成前均须验证

## L2 — 阶段门控 (7)

| 阶段  | Skill                                                                            | 触发               |
| ----- | -------------------------------------------------------------------------------- | ------------------ |
| 2规格 | [writing-plans](skills/writing-plans/SKILL.md)                                   | 原子级实施计划     |
| 2规格 | [spec-validation](skills/spec-validation/SKILL.md)                               | spec可验证验收标准 |
| 3执行 | [executing-plans](skills/executing-plans/SKILL.md)                               | 按计划逐步执行     |
| 3执行 | [subagent-driven-development](skills/subagent-driven-development/SKILL.md)       | 子Agent两阶段审查（默认关闭，显式触发）  |
| 3调试 | [systematic-debugging](skills/systematic-debugging/SKILL.md)                     | 根因分析/5Why      |
| 4验证 | [verification-before-completion](skills/verification-before-completion/SKILL.md) | 完成前交叉验证     |
| 3执行 | [test-driven-development](skills/test-driven-development/SKILL.md)               | RED-GREEN-REFACTOR（默认关闭，显式触发） |

## L3 — 信号触发 (34)

### 调研与决策

- [deep-research](skills/deep-research/SKILL.md) — L3 深度调研（Firecrawl+Exa+V1-V5验证）
- [adr-management](skills/adr-management/SKILL.md) — 架构决策记录管理
- [office-hours](skills/office-hours/SKILL.md) — 六问产品框架

### 审查与质量

- [requesting-code-review](skills/requesting-code-review/SKILL.md) — 请求代码审查
- [receiving-code-review](skills/receiving-code-review/SKILL.md) — 接收审查反馈
- [browser-qa](skills/browser-qa/SKILL.md) — 浏览器QA测试
- [autoplan](skills/autoplan/SKILL.md) — 自动CEO-Design-Eng审查流水线

### 设计与UI

- [design-pipeline](skills/design-pipeline/SKILL.md) — 设计管线（shotgun-对比板-HTML）
- [taste-memory](skills/taste-memory/SKILL.md) — 品味记忆学习（UI偏好跨会话）

### 上下文与记忆

- [context-engineering](skills/context-engineering/SKILL.md) — 上下文工程方法
- [memory-compression](skills/memory-compression/SKILL.md) — 上下文压缩与跨会话记忆
- [claude-mem-maintenance](skills/claude-mem-maintenance/SKILL.md) — claude-mem 记忆维护

### 代码架构

- [improve-codebase-architecture](skills/improve-codebase-architecture/SKILL.md) — 代码库架构改进
- [karpathy-guidelines](skills/karpathy-guidelines/SKILL.md) — Karpathy 四原则
- [structured-artifacts](skills/structured-artifacts/SKILL.md) — GSD 结构化制品管理

### 重构与技能治理

- [code-refactoring](skills/code-refactoring/SKILL.md) — 行为保持重构（圈复杂度/坏味道/安全重构）
- [frontend-refactor-proposer](skills/frontend-refactor-proposer/SKILL.md) — 前端局部重构 3 策略建议
- [frontend-library-advisor](skills/frontend-library-advisor/SKILL.md) — 前端 npm 库选型推荐
- [frontend-design-pattern-applier](skills/frontend-design-pattern-applier/SKILL.md) — 前端坏味道→设计模式重构
- [skill-creator](skills/skill-creator/SKILL.md) — 创建/更新有效技能指南
- [skill-reviewer](skills/skill-reviewer/SKILL.md) — skill 合规性审查
- [test-edge-case-analyzer](skills/test-edge-case-analyzer/SKILL.md) — 边界测试场景发现

### 执行与编排

- [workstream-management](skills/workstream-management/SKILL.md) — 并行任务流管理（git worktree）
- [using-git-worktrees](skills/using-git-worktrees/SKILL.md) — Git Worktree 并行开发
- [claude-to-deerflow](skills/claude-to-deerflow/SKILL.md) — deer-flow 外部编排引擎桥接

### Git与发布

- [git-workflow](skills/git-workflow/SKILL.md) — Git 工作流
- [pr-workflow](skills/pr-workflow/SKILL.md) — PR 工作流
- [ship](skills/ship/SKILL.md) — 发布管线
- [finishing-a-development-branch](skills/finishing-a-development-branch/SKILL.md) — 开发分支完成处理

### 优化与学习

- [caveman-compress](skills/caveman-compress/SKILL.md) — 输出压缩（caveman模式）
- [instinct-learning](skills/instinct-learning/SKILL.md) — 本能学习（Omega提示词优化器）
- [writing-skills](skills/writing-skills/SKILL.md) — 技能编写元技能

### 导航与引导

- [onboarding-guide](skills/onboarding-guide/SKILL.md) — 新人onboarding引导
- [triage](skills/triage/SKILL.md) — Bug分类（P0-P3）
